import os
import io
import time
import tempfile
from typing import Optional
from fastapi import FastAPI, Form, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, Response
from pydantic import BaseModel
import torch
import soundfile as sf
from gtts import gTTS

try:
    from qwen_tts import QwenTTS
    HAS_QWEN_TTS = True
except ImportError:
    HAS_QWEN_TTS = False

app = FastAPI(
    title="Qwen3-TTS Voice Cloning Microservice",
    description="FastAPI based Zero-Shot ICL Voice Cloning Container Service with Qwen3-TTS 1.7B",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
QWEN_MODEL_CACHE = None
REF_VOICE_DIR = os.getenv("REF_VOICE_DIR", "./ref_voices")


def load_qwen_tts_model():
    global QWEN_MODEL_CACHE
    if QWEN_MODEL_CACHE is not None:
        return QWEN_MODEL_CACHE

    print(f"[TTS Service] Initializing Qwen3-TTS 1.7B Model on [{DEVICE}]...", flush=True)
    if HAS_QWEN_TTS:
        try:
            model = QwenTTS.from_pretrained("Qwen/Qwen3-TTS-12Hz-1.7B", device=DEVICE)
            QWEN_MODEL_CACHE = model
            print(f"[TTS Service] Qwen3-TTS Model loaded successfully.", flush=True)
            return model
        except Exception as e:
            print(f"[TTS Service] Warning: Failed to load Qwen3-TTS from pretrained: {e}", flush=True)
    
    QWEN_MODEL_CACHE = "gtts_engine"
    return QWEN_MODEL_CACHE


@app.on_event("startup")
async def startup_event():
    print("=" * 60, flush=True)
    print(" [TTS Service] Starting Qwen3-TTS Voice Cloning Microservice ", flush=True)
    print(f" - Device      : {DEVICE}", flush=True)
    if DEVICE == "cuda":
        print(f" - GPU         : {torch.cuda.get_device_name(0)}", flush=True)
    print(f" - Ref Voice DB: {REF_VOICE_DIR}", flush=True)
    print("=" * 60, flush=True)
    os.makedirs(REF_VOICE_DIR, exist_ok=True)
    load_qwen_tts_model()


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {
        "status": "healthy",
        "service": "tts-service",
        "model": "Qwen3-TTS-12Hz-1.7B / gTTS Fallback",
        "device": DEVICE,
        "gpu_available": torch.cuda.is_available(),
        "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None
    }


class TTSRequest(BaseModel):
    text: str
    reference_audio_id: Optional[str] = "default_owner"
    language: Optional[str] = "ko"


@app.post("/api/v1/tts/clone")
async def clone_voice_and_synthesize(req: TTSRequest):
    text = req.text
    reference_audio_id = req.reference_audio_id or "default_owner"
    language = req.language or "ko"

    if not text or not text.strip():
        text = "음성이 잘 들리지 않았습니다. 다시 말씀해 주세요."

    print(f"\n[TTS Service] 🗣️ Synthesizing Speech for Text: '{text}'", flush=True)
    start_time = time.time()
    
    ref_audio_path = os.path.join(REF_VOICE_DIR, f"{reference_audio_id}.wav")
    has_ref_audio = os.path.exists(ref_audio_path)

    sample_rate = 24000
    model = load_qwen_tts_model()

    try:
        if HAS_QWEN_TTS and hasattr(model, "generate_voice_clone"):
            audio_data = model.generate_voice_clone(
                text=text,
                ref_audio_path=ref_audio_path if has_ref_audio else None,
                language=language
            )
            buf = io.BytesIO()
            sf.write(buf, audio_data, sample_rate, format="WAV")
            buf.seek(0)
        else:
            # High quality Korean Speech via gTTS (Replaces Sine Beep Tone)
            print(f"[TTS Service] 🎙️ Generating Natural Korean Voice via gTTS Engine...", flush=True)
            tts = gTTS(text=text, lang='ko')
            mp3_buf = io.BytesIO()
            tts.write_to_fp(mp3_buf)
            mp3_buf.seek(0)

            # Convert mp3 buffer to wav format via soundfile/librosa
            import librosa
            audio_data, sr = librosa.load(mp3_buf, sr=sample_rate)
            buf = io.BytesIO()
            sf.write(buf, audio_data, sample_rate, format="WAV")
            buf.seek(0)

        synth_time = time.time() - start_time
        print(f"[TTS Service] ✅ Speech Synthesized in {synth_time:.2f}s (Text length: {len(text)})", flush=True)

        headers = {
            "X-Inference-Time-Seconds": str(round(synth_time, 3)),
            "X-Compute-Device": DEVICE,
            "X-Ref-Audio-Used": str(has_ref_audio),
            "X-Voice-ID": reference_audio_id
        }

        return StreamingResponse(buf, media_type="audio/wav", headers=headers)

    except Exception as e:
        print(f"[TTS Service Error] Synthesis exception: {e}", flush=True)
        raise HTTPException(status_code=500, detail=f"Voice Synthesis Error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8003, reload=False)
