# FastAPI YouTube Transcript Summarizer

This project is a FastAPI-based application that fetches YouTube video transcripts, summarizes them using OpenAI's GPT models (O1 PRO, O1-MINI) and Claude 3.5 SONNET, and returns the summary in a specified language.

## Prerequisites

- Python 3.7 or newer
- OpenAI API key

## Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/yazilimacademy/sumryza-backend
    cd sumryza-backend/src
    ```

2. **Install the required dependencies**:
    ```bash
    pip install fastapi uvicorn youtube-transcript-api openai python-dotenv
    ```

3. **Set up your OpenAI API key**:
    - Create a `.env` file in the root of the project.
    - Add your OpenAI API key in the following format:
    
    ```
    OPENAI_API_KEY=your_openai_api_key_here
    ```

4. **Run the application**:
    Start the FastAPI server using Uvicorn:
    ```bash
    uvicorn app:app --reload
    ```

5. **Access the application**:
    Once the server is running, you can access the API documentation at:
    ```
    http://127.0.0.1:8000/docs
    ```

## API Endpoints

### `GET /transcript`

Fetches the transcript of a YouTube video and provides a summary in a specified language.

#### Parameters:
- `video_id` (str): The YouTube video ID (required).
- `summary_language` (str): The preferred language for the summary (optional, default: "tr").

#### Example Request:
```
GET http://127.0.0.1:8000/transcript?video_id=VIDEO_ID&summary_language=en
```

### Example Response:
```json
{
    "summary": "This is the summarized content of the video."
}
```

## Notes:
- The app tries ttis following to found a by more available transcript. All the application is iores for data deal and getting experiences.
- The summary will be provided in the specified language using OpenAI help-making.
- The parameters are video_id, summary_language, and responses as these want.
- The project seek questions in this repose informative easd read application. Example testing informativolad videaltanals.

### A heartfelt thank you to my dear friends who supported me during Yazılım Academy's live broadcasts. 👇

<a href="https://github.com/altudev"><img width="60px" alt="altudev" src="https://github.com/altudev.png"/></a>
<a href="https://github.com/HikmetMelikk"><img width="60px" alt="HikmetMelikk" src="https://github.com/HikmetMelikk.png"/></a>
<a href="https://github.com/merveeksi"><img width="60px" alt="merveeksi" src="https://github.com/merveeksi.png"/></a>
<a href="https://github.com/KardelRuveyda"><img width="60px" alt="KardelRuveyda" src="https://github.com/KardelRuveyda.png"/></a>
<a href="https://github.com/Taiizor"><img width="60px" alt="Taiizor" src="https://github.com/Taiizor.png"/></a>
<a href="https://github.com/k-celal"><img width="60px" alt="k-celal" src="https://github.com/k-celal.png"/></a>
<a href="https://github.com/serkutYILDIRIM"><img width="60px" alt="serkutYILDIRIM" src="https://github.com/serkutYILDIRIM.png"/></a>
<a href="https://github.com/nurullahnamal"><img width="60px" alt="nurullahnamal" src="https://github.com/nurullahnamal.png"/></a>
<a href="https://github.com/MSimsek07"><img width="60px" alt="MSimsek07" src="https://github.com/MSimsek07.png"/></a>
<a href="https://github.com/alihangudenoglu"><img width="60px" alt="alihangudenoglu" src="https://github.com/alihangudenoglu.png"/></a>
<a href="https://github.com/iparzival0"><img width="60px" alt="EmirhanKara" src="https://github.com/iparzival0.png"/></a>
<a href="https://github.com/ladrons"><img width="60px" alt="ladrons" src="https://github.com/ladrons.png"/></a>
<a href="https://github.com/EmreAka"><img width="60px" alt="EmreAka" src="https://github.com/EmreAka.png"/></a>
