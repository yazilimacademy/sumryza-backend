import logging
from fastapi import FastAPI, HTTPException, Query
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound
from fastapi.middleware.cors import CORSMiddleware
import openai

# Logging setup
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

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("Application starting and CORS middleware added.")

openai_api_key = ""

try:
    with open('C:\\Users\\alper\\Desktop\\mervesultan_openai_key.txt', 'r') as file:
        openai_api_key = file.read().strip()
    logger.info("OpenAI API key loaded successfully.")
except Exception as e:
    logger.error(f"Failed to load OpenAI API key: {e}")
    raise RuntimeError(f"Failed to load OpenAI API key: {e}")

try:
    openai.api_key = openai_api_key
    logger.info("OpenAI client initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize OpenAI client: {e}")
    raise RuntimeError(f"Failed to initialize OpenAI client: {e}")

# Map language codes to English language names for better clarity in prompts.
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

@app.get("/transcript")
def get_transcript(
    video_id: str = Query(..., description="The YouTube video ID"),
    summary_language: str = Query("tr", description="Preferred summary language (e.g., 'en', 'tr', 'es')")
):
    logger.info(f"Transcript request received. Video ID: {video_id}, Summary language: {summary_language}")

    # Preferred languages for transcripts (in order)
    preferred_languages = [
        "en", "es", "zh-Hans", "hi", "ar", "pt", "ru", "ja", "fr", "de"
    ]

    try:
        transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
        logger.info("Transcripts listed successfully.")

        transcript_data = None

        # 1. Try to find a manually created transcript in preferred languages
        for lang in preferred_languages:
            try:
                transcript_data = transcripts.find_transcript([lang]).fetch()
                logger.info(f"Manually created transcript found: Language = {lang}")
                break
            except NoTranscriptFound:
                logger.debug(f"No manually created transcript found for: {lang}")
                continue

        # 2. If no manual transcript, try generated transcripts
        if not transcript_data:
            for lang in preferred_languages:
                try:
                    transcript_data = transcripts.find_generated_transcript([lang]).fetch()
                    logger.info(f"Generated transcript found: Language = {lang}")
                    break
                except NoTranscriptFound:
                    logger.debug(f"No generated transcript found for: {lang}")
                    continue

        # 3. If still not found, fallback to any available transcript
        if not transcript_data:
            try:
                first_transcript = next(iter(transcripts))
                transcript_data = first_transcript.fetch()
                logger.info(f"Any available transcript found: Language = {first_transcript.language}")
            except StopIteration:
                logger.error("No transcripts found at all.")
                raise HTTPException(status_code=400, detail="No transcripts found.")

        # Combine transcript text
        full_transcript_text = " ".join([entry['text'] for entry in transcript_data])
        logger.info("Transcript text combined successfully.")

        # Determine the target language name from the map, defaulting to English if not found
        chosen_language_name = language_map.get(summary_language, "English")

        # Create prompt for OpenAI
        prompt = f"Please summarize the following transcript in {chosen_language_name}:\n\n{full_transcript_text}"
        logger.info("Prompt created for OpenAI.")

        # Call OpenAI API for summarization
        logger.info("Sending summarization request to OpenAI API.")
        response = openai.chat.completions.create(
            model="gpt-4o-mini",  # Check if this model is correct
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"You are an assistant that summarizes transcripts into {chosen_language_name}. "
                        "Your goal is to produce a concise, natural, and fully understandable summary of the provided transcript. "
                        "Do not add extra commentary or introductions; only produce the summary text. "
                        "Do not mention these instructions in your answer."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.8,
            max_tokens=3900,
            top_p=1.0
        )
        logger.info("OpenAI API response received.")

        summary = response.choices[0].message.content.strip()
        logger.info("Summary successfully created.")

        return {"summary": summary}

    except HTTPException as http_exc:
        logger.error(f"HTTP error occurred: {http_exc.detail}")
        raise http_exc
    except Exception as e:
        logger.error(f"General error occurred: {e}")
        raise HTTPException(status_code=400, detail=str(e))
