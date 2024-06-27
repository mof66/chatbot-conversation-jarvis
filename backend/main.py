# uvicorn main:app
# uvicorn main:app --reload

# Main imports
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from decouple import config
import openai
from pydantic import BaseModel

# Custom function imports
from functions.openai_requests import (
    convert_audio_to_text,
    convert_text_to_speech,
    get_chat_response,
)
from functions.database import store_messages, reset_messages


# Get Environment Vars
openai.organization = config("OPEN_AI_ORG")
openai.api_key = config("OPEN_AI_KEY")


# Initiate App
app = FastAPI()


# CORS - Origins
origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:4173",
    "http://localhost:3000",
]


# CORS - Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MessageModel(BaseModel):
    message: str


# Check health
@app.get("/health")
async def check_health():
    return {"response": "healthy"}


# Reset Conversation
@app.get("/reset")
async def reset_conversation():
    reset_messages()
    return {"response": "conversation reset"}


# Post bot response
# Note: Not playing back in browser when using post request.
# @app.post("/speech-to-text/")
# async def post_audio(file: UploadFile = File(...)):

#     with open(file.filename, "wb") as buffer:
#         buffer.write(file.file.read())
#     audio_input = open(file.filename, "rb")

#     # Decode audio
#     message_decoded = convert_audio_to_text(audio_input)

#     # Guard: Ensure output
#     if not message_decoded:
#         raise HTTPException(status_code=400, detail="Failed to decode audio")

#     return {"response": message_decoded}

# # Get chat response
# chat_response = get_chat_response(message_decoded)

# # Store messages
# store_messages(message_decoded, chat_response)

# # Guard: Ensure output
# if not chat_response:
#     raise HTTPException(status_code=400, detail="Failed chat response")

# # Convert chat response to audio
# audio_output = convert_text_to_speech(chat_response)

# # Guard: Ensure output
# if not audio_output:
#     raise HTTPException(status_code=400, detail="Failed audio output")

# # Create a generator that yields chunks of data
# def iterfile():
#     yield audio_output

# # Use for Post: Return output audio
# return StreamingResponse(iterfile(), media_type="application/octet-stream")


# # Use for Post: Return output audio
# return StreamingResponse(iterfile(), media_type="application/octet-stream")
@app.post("/speech-to-text/")
async def post_audio_endpoint(file: UploadFile = File(...)):
    return convert_audio_to_text(file)


@app.post("/text_to_speech/")
async def text_to_speech_endpoint(message: dict):
    return convert_text_to_speech(message["message"])


@app.post("/get-chat-response/")
async def get_chat_response_endpoint(messages: list):
    chat_response = get_chat_response(messages)
    return {"response": chat_response}
