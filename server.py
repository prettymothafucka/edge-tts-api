from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
import edge_tts
import uuid
import os

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Edge-TTS API running"}

@app.post("/v1/audio/speech")
async def text_to_speech(request: Request):
    data = await request.json()
    text = data.get("text", "")
    voice = data.get("voice", "en-US-AriaNeural")

    # Create audio folder if missing
    os.makedirs("audio", exist_ok=True)

    # Generate filename
    filename = f"audio/{uuid.uuid4()}.mp3"

    # Generate speech
    tts = edge_tts.Communicate(text, voice)
    await tts.save(filename)

    # Return URL and success message
    base_url = str(request.base_url).rstrip("/")
    audio_url = f"{base_url}/audio/{os.path.basename(filename)}"
    return JSONResponse({"message": "Speech generated successfully", "audio_url": audio_url})

@app.get("/audio/{filename}")
async def get_audio(filename: str):
    file_path = f"audio/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="audio/mpeg")
    return JSONResponse({"error": "File not found"}, status_code=404)
