import chainlit as cl
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

client = openai.AsyncOpenAI()

cl.instrument_openai()

settings = {
    "model": "gpt-3.5-turbo",
    "temperature": 0,
}

@cl.on_chat_start
async def start():
    await cl.Message(content="Hello! I'm your travel agent chatbot. How can I assist you today?").send()

@cl.on_message
async def handle_message(message: cl.Message):
    # TBD
    response = await client.chat.completions.create(
        messages=[
            {
                "content": "You are a travel agent who helps users plan their trips.",
                "role": "system"
            },
            {
                "content": message.content,
                "role": "user"
            }
        ],
        **settings
    )

    await cl.Message(content=response.choices[0].message.content).send()