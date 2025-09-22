import chainlit as cl
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

client = openai.AsyncOpenAI()
cl.instrument_openai()

settings = {
    "model": "gpt-3.5-turbo",
    "temperature": 0.7,
    "max_tokens": 500,
    "top_p": 1,
    "frequency_penalty": 0.5,
    "presence_penalty": 0.5,
}

chat_history = []

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
async def on_action(action: cl.Action):
    user_message = action.payload["value"]
    await handle_message(cl.Message(content=user_message))


@cl.action_callback("nature")
async def on_action(action: cl.Action):
    user_message = action.payload["value"]
    await handle_message(cl.Message(content=user_message))


@cl.action_callback("solo")
async def on_action(action: cl.Action):
    user_message = action.payload["value"]
    await handle_message(cl.Message(content=user_message))


@cl.on_message
async def handle_message(message: cl.Message):

    chat_history.append({"role": "user", "content": message.content})

    messages = [{"role": "system", "content": "You are a travel agent who helps users plan their trips."}] + chat_history
    
    stream = await client.chat.completions.create(
        messages=messages, stream=True, **settings
    )

    msg = cl.Message(content="") # creates empty message to begin streaming
    await msg.send()

    full_reply = "" # logs full reply to append to chat history

    async for part in stream:
        if token := part.choices[0].delta.content:
            full_reply += token
            await msg.stream_token(token)

    await msg.update() # completes the message stream

    chat_history.append({"role": "assistant", "content": full_reply})