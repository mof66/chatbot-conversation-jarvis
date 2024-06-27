import shutil
from tempfile import NamedTemporaryFile
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
import openai
from decouple import config
import io

from functions.database import get_recent_messages


# Retrieve Environment Variables
openai.organization = config("OPEN_AI_ORG")
openai.api_key = config("OPEN_AI_KEY")


# Open AI - Whisper
# Convert audio to text
def convert_audio_to_text(file):
    # Ensure the file is in a supported format for OpenAI's Whisper model
    supported_formats = (
        ".flac",
        ".mp3",
        ".mp4",
        ".mpeg",
        ".mpga",
        ".ogg",
        ".wav",
        ".webm",
    )
    if not file.filename.endswith(supported_formats):
        raise HTTPException(status_code=400, detail="Unsupported file format")

    # Save the uploaded file to a temporary file
    with NamedTemporaryFile(delete=False, suffix=file.filename) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    # Call OpenAI API for transcription
    try:
        with open(tmp_path, "rb") as audio_file:
            transcript_response = openai.audio.transcriptions.create(
                model="whisper-1", file=audio_file, response_format="json"
            )
    except Exception as e:
        # Handle potential errors from the API call
        raise HTTPException(status_code=500, detail=str(e))

    # Extract the transcription text from the response
    message_decoded = transcript_response.text

    # Guard: Ensure output
    if not message_decoded:
        raise HTTPException(status_code=400, detail="Failed to decode audio")

    return {"response": message_decoded}


def convert_text_to_speech(message):
    try:
        response = openai.audio.speech.create(
            model="tts-1-hd",
            voice="alloy",
            input=message,
        )
        audio_data = response.content
        return StreamingResponse(io.BytesIO(audio_data), media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Open AI - Chat GPT
# Convert audio to text
def get_chat_response(messages):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages
        )
        message_text = response.choices[0].message
        return message_text
    except Exception as e:
        return
