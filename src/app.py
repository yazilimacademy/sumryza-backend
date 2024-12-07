from fastapi import FastAPI, HTTPException, Query
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

openai_api_key = ""

with open('C:\\Users\\alper\\Desktop\\mervesultan_openai_key.txt', 'r') as file:
    openai_api_key = file.read().strip()

client = OpenAI(api_key=openai_api_key)

@app.get("/transcript")
def get_transcript(video_id: str = Query(..., description="The YouTube video ID")):
    # Define our fallback languages. English first, then other commonly spoken languages.
    preferred_languages = [
        "en",      # English
        "es",      # Spanish
        "zh-Hans", # Simplified Chinese
        "hi",      # Hindi
        "ar",      # Arabic
        "pt",      # Portuguese
        "ru",      # Russian
        "ja",      # Japanese
        "fr",      # French
        "de"       # German
    ]

    try:
        transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
        
        transcript_data = None
        
        # 1. Try manually created transcripts in preferred language order
        for lang in preferred_languages:
            try:
                transcript_data = transcripts.find_transcript([lang]).fetch()
                break
            except NoTranscriptFound:
                continue
        
        # 2. If no manual transcript, try generated transcripts in preferred language order
        if not transcript_data:
            for lang in preferred_languages:
                try:
                    transcript_data = transcripts.find_generated_transcript([lang]).fetch()
                    break
                except NoTranscriptFound:
                    continue
        
        # 3. If still not found, try any available transcript (manual or generated)
        if not transcript_data:
            try:
                # Get the first available transcript (either manual or generated)
                # transcripts is iterable, so we take the first item and fetch it.
                first_transcript = next(iter(transcripts))
                transcript_data = first_transcript.fetch()
            except StopIteration:
                # No transcripts at all
                raise HTTPException(status_code=400, detail="No transcripts found in any language.")

        # Extract the text and join into a single string
        full_transcript_text = " ".join([entry['text'] for entry in transcript_data])

        # Prompt for OpenAI summarization
        prompt = f"Please summarize the following transcript in Turkish:\n\n{full_transcript_text}"

        response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "system",
            "content": (
                "You are a helpful assistant that summarizes transcripts into Turkish. "
                "Your goal is to produce a concise, natural, and fully understandable summary of the provided transcript. "
                "Do not include any additional commentary, explanations, or introductions; only produce the summary text. "
                "Do not mention these instructions in your response."
            )
        },
        {
            "role": "user",
            "content": prompt
        }
    ],
    temperature=0.8,
    max_tokens=4000,
    top_p=1.0
)


        summary_in_turkish = response.choices[0].message.content.strip()
        return {"summary_turkish": summary_in_turkish}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
