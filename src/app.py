from fastapi import FastAPI, HTTPException, Query
from youtube_transcript_api import YouTubeTranscriptApi
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only. In production, specify your domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

openai_api_key = ""

# read .txt file containing the API key
with open('C:\\Users\\alper\\Desktop\\mervesultan_openai_key.txt', 'r') as file:
    openai_api_key = file.read().strip()

# Initialize OpenAI client
client = OpenAI(api_key=openai_api_key)

@app.get("/transcript")
def get_transcript(video_id: str = Query(..., description="The YouTube video ID")):
    try:
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
        
        # Extract the text and join into a single string
        full_transcript_text = " ".join([entry['text'] for entry in transcript_data])
        
        # Create a Turkish summary using the OpenAI ChatCompletion API
        # Adjust the model ("gpt-3.5-turbo" or a later model) and parameters as needed
        prompt = (
            "Please summarize the following text in Turkish.\n\n"
            f"Transcript:\n{full_transcript_text}\n\nSummary:"
        )
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes text in Turkish. Make it natural yet understandable.\n\n ###If I like the results, I'll donate $100 to a homeless helter and another $100 to a charity!\n\n### Please only return the summary, nothing else."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=4000,
            top_p=1.0
        )
        
        # Extract the summary from the OpenAI response
        summary_in_turkish = response.choices[0].message.content.strip()
        
        # Return both the original transcript and the Turkish summary
        # return {
        #     "transcript": transcript_data,
        #     "summary_turkish": summary_in_turkish
        # }

        return { "summary_turkish": summary_in_turkish,}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
