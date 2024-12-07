import logging
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound
from fastapi.middleware.cors import CORSMiddleware
import openai
from ollama import chat
from ollama import ChatResponse
from data.prompts import get_summary_prompt, get_key_points_prompt
import anthropic


api_key_path = "C:\\Users\\alper\\Desktop\\claude_api_key.txt"

anthropic_api_key = ""

with open(api_key_path, "r") as file:
    anthropic_api_key = file.read().strip()

# Logging setup
def setup_logging():
    logger = logging.getLogger("app_logger")
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_format)

    file_handler = logging.FileHandler("app.log", encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_format)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

logger = setup_logging()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("Application starting and CORS middleware added.")

# # Load .env file
# load_dotenv()

# # Load OpenAI API key from environment variable
# openai_api_key = os.getenv("OPENAI_API_KEY")
# if not openai_api_key:
#     logger.error("OpenAI API key is missing.")
#     raise RuntimeError("OpenAI API key is missing.")

# try:
#     openai.api_key = openai_api_key
#     logger.info("OpenAI client initialized successfully.")
# except Exception as e:
#     logger.error(f"Failed to initialize OpenAI client: {e}")
#     raise RuntimeError(f"Failed to initialize OpenAI client: {e}")

# Map language codes to English language names for better clarity in prompts
language_map = {
    "en": "English",
    "tr": "Turkish",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "hi": "Hindi",
    "ar": "Arabic",
    "pt": "Portuguese",
    "ru": "Russian",
    "ja": "Japanese",
    "zh-Hans": "Simplified Chinese"
}

# Fetch transcript function
def fetch_transcript(video_id, preferred_languages):
    try:
        transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
        logger.info("Transcripts listed successfully.")
        transcript_data = None

        # Try to find a manually created transcript in preferred languages
        for lang in preferred_languages:
            try:
                transcript_data = transcripts.find_transcript([lang]).fetch()
                logger.info(f"Manually created transcript found: Language = {lang}")
                break
            except NoTranscriptFound:
                logger.debug(f"No manually created transcript found for: {lang}")
                continue

        # Try to find a generated transcript in preferred languages
        if not transcript_data:
            for lang in preferred_languages:
                try:
                    transcript_data = transcripts.find_generated_transcript([lang]).fetch()
                    logger.info(f"Generated transcript found: Language = {lang}")
                    break
                except NoTranscriptFound:
                    logger.debug(f"No generated transcript found for: {lang}")
                    continue

        # Fallback to any available transcript if none of the above worked
        if not transcript_data:
            try:
                first_transcript = next(iter(transcripts))
                transcript_data = first_transcript.fetch()
                logger.info(f"Any available transcript found: Language = {first_transcript.language}")
            except StopIteration:
                logger.error("No transcripts found at all.")
                raise HTTPException(status_code=400, detail="No transcripts found.")
        return transcript_data
    except Exception as e:
        logger.error(f"Error fetching transcript: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/transcript")
def get_transcript(
    video_id: str = Query(..., description="The YouTube video ID"),
    summary_language: str = Query("tr", description="Preferred summary language (e.g., 'en', 'tr', 'es')")
):
    logger.info(f"Transcript request received. Video ID: {video_id}, Summary language: {summary_language}")

    if summary_language not in language_map:
        logger.warning(f"Invalid language code: {summary_language}. Defaulting to 'en'.")
        summary_language = "en"

    preferred_languages = [
        "en", "es", "zh-Hans", "hi", "ar", "pt", "ru", "ja", "fr", "de"
    ]

    try:
        transcript_data = fetch_transcript(video_id, preferred_languages)
        full_transcript_text = " ".join([entry['text'] for entry in transcript_data])
        logger.info("Transcript text combined successfully.")

        chosen_language_name = language_map.get(summary_language, "English")
        logger.info(f"Chosen language name: {chosen_language_name}")

        client = anthropic.Anthropic(api_key=anthropic_api_key)

        prompt = f"Summarize the following transcript in {chosen_language_name}:\n\n{full_transcript_text}"

        message = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=4000,
            temperature=0.2,
            system=get_summary_prompt(chosen_language_name),
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        )

        summary = message.content[0].text

        # messages = [
        #     {
        #         'role': 'system',
        #         'content': get_summary_prompt(chosen_language_name)
        #     },
        #     {
        #         'role': 'user',
        #         'content': prompt
        #     }
        # ]

        # logger.info("Sending summarization request to Ollama.")
        # response: ChatResponse = chat(model='mistral-small:latest', messages=messages)

        # summary = response.message.content.strip()
        # logger.info("Summary successfully created.")

        return {"summary": summary}

    except HTTPException as http_exc:
        logger.error(f"HTTP error occurred: {http_exc.detail}")
        raise http_exc
    except Exception as e:
        logger.error(f"General error occurred: {e}")
        raise HTTPException(status_code=400, detail=str(e))