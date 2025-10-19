import os
import uuid
from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import edge_tts

app = FastAPI()

# Allow CORS (for testing — make it specific later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Edge-TTS API running"}

async def synthesize_to_file(text: str, voice: str, filename: str):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(filename)

@app.post("/v1/audio/speech")
async def speech(request: Request, background_tasks: BackgroundTasks):
    content_type = request.headers.get("content-type", "")
    if content_type.startswith("application/json"):
        payload = await request.json()
        text = payload.get("text")
        voice = payload.get("voice", "en-US-AriaNeural")
    else:
        form = await request.form()
        text = form.get("text")
        voice = form.get("voice", "en-US-AriaNeural")

    if not text:
        raise HTTPException(status_code=400, detail="Missing 'text' field")

    uid = uuid.uuid4().hex
    filename = f"/tmp/edge_tts_{uid}.mp3"

    try:
        await synthesize_to_file(text, voice, filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    background_tasks.add_task(lambda p=filename: os.remove(p) if os.path.exists(p) else None)
    return FileResponse(filename, media_type="audio/mpeg", filename=f"speech_{uid}.mp3")
