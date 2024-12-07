import logging
from fastapi import FastAPI, HTTPException, Query
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound
from fastapi.middleware.cors import CORSMiddleware
import openai  # OpenAI kütüphanesi genellikle bu şekilde kullanılır

# Loglama yapılandırması
logger = logging.getLogger("app_logger")
logger.setLevel(logging.DEBUG)

# Konsol için loglayıcı
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_format)

# Dosya için loglayıcı
file_handler = logging.FileHandler("app.log", encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_format)

# Loglayıcıları ekleme
logger.addHandler(console_handler)
logger.addHandler(file_handler)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Üretimde, kendi alan adlarınızı belirtin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("Uygulama başlatılıyor ve CORS middleware ekleniyor.")

openai_api_key = ""

try:
    with open('C:\\Users\\alper\\Desktop\\mervesultan_openai_key.txt', 'r') as file:
        openai_api_key = file.read().strip()
    logger.info("OpenAI API anahtarı başarıyla yüklendi.")
except Exception as e:
    logger.error(f"OpenAI API anahtarı yüklenemedi: {e}")
    raise RuntimeError(f"OpenAI API anahtarı yüklenemedi: {e}")

try:
    openai.api_key = openai_api_key
    logger.info("OpenAI client başarıyla başlatıldı.")
except Exception as e:
    logger.error(f"OpenAI client başlatılamadı: {e}")
    raise RuntimeError(f"OpenAI client başlatılamadı: {e}")

@app.get("/transcript")
def get_transcript(video_id: str = Query(..., description="YouTube video ID'si")):
    logger.info(f"Transkript isteği alındı. Video ID: {video_id}")

    preferred_languages = [
        "en",       # İngilizce
        "es",       # İspanyolca
        "zh-Hans",  # Basitleştirilmiş Çince
        "hi",       # Hintçe
        "ar",       # Arapça
        "pt",       # Portekizce
        "ru",       # Rusça
        "ja",       # Japonca
        "fr",       # Fransızca
        "de"        # Almanca
    ]

    try:
        transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
        logger.info("Transkriptler başarıyla listelendi.")

        transcript_data = None

        # 1. Tercih edilen dillerde manuel oluşturulmuş transkriptleri bulma
        for lang in preferred_languages:
            try:
                transcript_data = transcripts.find_transcript([lang]).fetch()
                logger.info(f"Manuel transkript bulundu: Dil = {lang}")
                break
            except NoTranscriptFound:
                logger.debug(f"Manuel transkript bulunamadı: Dil = {lang}")
                continue

        # 2. Manuel transkript bulunamazsa, tercih edilen dillerde oluşturulmuş transkriptleri bulma
        if not transcript_data:
            for lang in preferred_languages:
                try:
                    transcript_data = transcripts.find_generated_transcript([lang]).fetch()
                    logger.info(f"Oluşturulmuş transkript bulundu: Dil = {lang}")
                    break
                except NoTranscriptFound:
                    logger.debug(f"Oluşturulmuş transkript bulunamadı: Dil = {lang}")
                    continue

        # 3. Hala transkript bulunamazsa, mevcut herhangi bir transkripti kullanma
        if not transcript_data:
            try:
                first_transcript = next(iter(transcripts))
                transcript_data = first_transcript.fetch()
                logger.info(f"Herhangi bir transkript bulundu: Dil = {first_transcript.language}")
            except StopIteration:
                logger.error("Hiçbir transkript bulunamadı.")
                raise HTTPException(status_code=400, detail="Hiçbir transkript bulunamadı.")

        # Transkript metnini birleştirme
        full_transcript_text = " ".join([entry['text'] for entry in transcript_data])
        logger.info("Transkript metni başarıyla birleştirildi.")

        # OpenAI özeti için istem oluşturma
        prompt = f"Lütfen aşağıdaki transkripti Türkçe olarak özetleyin:\n\n{full_transcript_text}"
        logger.info("OpenAI özeti için istem oluşturuldu.")

        # OpenAI API çağrısı
        logger.info("OpenAI API'sine özetleme isteği gönderiliyor.")
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Model adını kontrol edin
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Sen, transkriptleri Türkçeye özetleyen yardımcı bir asistansın. "
                        "Amacın, sağlanan transkriptin özlü, doğal ve tamamen anlaşılır bir özetini üretmektir. "
                        "Ek yorum, açıklama veya giriş ekleme; yalnızca özet metnini üret. "
                        "Bu talimatları cevabında belirtme."
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
        logger.info("OpenAI API yanıtı alındı.")

        summary_in_turkish = response.choices[0].message.content.strip()
        logger.info("Özet başarıyla oluşturuldu.")

        return {"summary_turkish": summary_in_turkish}

    except HTTPException as http_exc:
        logger.error(f"HTTP hatası oluştu: {http_exc.detail}")
        raise http_exc
    except Exception as e:
        logger.error(f"Genel bir hata oluştu: {e}")
        raise HTTPException(status_code=400, detail=str(e))
