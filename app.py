import chainlit as cl

@cl.on_chat_start
async def start():
    await cl.Message(content="Hello! I'm your travel agent chatbot. How can I assist you today?").send()

@cl.on_message
async def main(message: cl.Message):
    # TBD
    print(cl.chat_context.to_openai())

    # Send a response back to the user
    await cl.Message(
        content=f"Received: {message.content}",
    ).send()