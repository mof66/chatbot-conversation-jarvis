import requests
import openai
from decouple import config

openai.organization = config("OPEN_AI_ORG")
openai.api_key = config("OPEN_AI_KEY")


# Open AI
# Convert text to speech
def convert_text_to_speech(message):
    print("Converting text to speech", message)
    # body = {"text": message, "voice_settings": {"stability": 0, "similarity_boost": 0}}

    try:
        response = openai.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=message,
        )
        if response.status_code == 200:

            return response.content
        else:
            return
    except Exception as e:
        return
