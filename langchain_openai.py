import os
import chainlit as cl

from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.schema import HumanMessage

from langchain.document_loaders import WebBaseLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import format_document
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI

from langchain_core.runnables import RunnablePassthrough, RunnableLambda, RunnableMap
from langchain.callbacks.streaming_aiter import AsyncIteratorCallbackHandler
import asyncio

callback = AsyncIteratorCallbackHandler()

# scraping from wikivoyage.org due to its permissions being lenient 
wikivoyage = [
    "https://en.wikivoyage.org/wiki/Budget_travel",
    "https://en.wikivoyage.org/wiki/Culture_shock",
    "https://en.wikivoyage.org/wiki/Travelling_alone",
    "https://en.wikivoyage.org/wiki/Europe",
    "https://en.wikivoyage.org/wiki/North_America",
    "https://en.wikivoyage.org/wiki/Asia",
    "https://en.wikivoyage.org/wiki/South_America",
    "https://en.wikivoyage.org/wiki/Africa",
    "https://en.wikivoyage.org/wiki/Australia"
]

def format_docs(docs):
    return "\n\n".join([doc.page_content for doc in docs])

loader = WebBaseLoader(wikivoyage)
docs = loader.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500, 
    chunk_overlap=50,
    separators=["\n\n", "\n", " ", ""])
chunks = splitter.split_documents(docs)

embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(chunks, embeddings)
retriever = vectorstore.as_retriever()

memory = ConversationBufferMemory(return_messages=True)

@cl.on_chat_start
async def start():
    actions=[
            cl.Action(name="budget", label="💸 Budget-friendly destinations", payload={"value": "Can you suggest some budget-friendly travel destinations under $1000?"}),
            cl.Action(name="nature", label="🌲 Nature travel spots", payload={"value": "Can you recommend some nature travel spots?"}),
            cl.Action(name="solo", label="🧳 Tips for solo travelers", payload={"value": "What are some tips for solo travelers?"})
        ]  
    await cl.Message(
        content="Hello! I'm your travel agent chatbot. Let me know how I can assist you, or choose a topic to get started:", actions=actions    
    ).send()


@cl.action_callback("budget")
@cl.action_callback("nature")
@cl.action_callback("solo")
async def on_action(action: cl.Action):
    user_message = action.payload["value"]
    await handle_message(cl.Message(content=user_message))

@cl.on_message
async def handle_message(message: cl.Message):

    callback = AsyncIteratorCallbackHandler()

    # streaming with callback
    llm = ChatOpenAI(
        model_name="gpt-3.5-turbo", 
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.7,
        max_tokens=500,
        streaming=True,
        callbacks=[callback]
    )

    # rag_chain = (
    #     RunnableMap({
    #     "context": retriever | RunnableLambda(format_docs),
    #     "question": RunnablePassthrough()
    #     }) | RunnableLambda(lambda x: f"Context:\n{x['context']}\n\nQuestion: {x['question']}") | llm
    # )

    memory.chat_memory.add_user_message(message.content)

    msg = cl.Message(content="") # creates empty message to begin streaming
    await msg.send()

    docs = await retriever.ainvoke(message.content) 
    context = format_docs(docs)
    prompt = f"Context:\n{context}\n\nQuestion: {message.content}"
    task = asyncio.create_task(llm.ainvoke([HumanMessage(content=prompt)]))

    async for token in callback.aiter():
        print(token, end="", flush=True)
        await msg.stream_token(token)

    result = await task
    memory.chat_memory.add_ai_message(result.content)
    await msg.update() # completes the message stream}
