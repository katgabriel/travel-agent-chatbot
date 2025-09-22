import chainlit as cl
import requests
import json
import httpx

OLLAMA_URL = "http://localhost:11434/api/generate"

MODEL_NAME = "mistral"

chat_history = []

async def call_ollama(message: str) -> str:

    payload = {
        "model": MODEL_NAME,
        "prompt": message,
        "stream": False
    }

    print("Sending payload to Ollama:", payload)

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(OLLAMA_URL, json=payload)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "Sorry, I couldn't generate a response.")
    except httpx.RequestError as e:
        return f"Error connecting to Ollama: {str(e)}"
    except json.JSONDecodeError:
        return "Error: Invalid response from Ollama."
    

@cl.on_chat_start
async def start():
    actions=[
            cl.Action(name="budget", label="💸 Budget-friendly destinations", payload={"value": "List 3 travel destinations under $1000."}),
            cl.Action(name="nature", label="🌲 Nature travel spots", payload={"value": "List 3 travel spots."}),
            cl.Action(name="solo", label="🧳 Tips for solo travelers", payload={"value": "List 3 tips for solo travelers."})
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
    user_message = message.content
    reply = await call_ollama(user_message)
    await cl.Message(content=reply).send()