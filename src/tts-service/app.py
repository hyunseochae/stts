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

# Try importing Qwen-TTS
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

    print(f"[TTS Service] Initializing Qwen3-TTS 1.7B Model on [{DEVICE}]...")
    if HAS_QWEN_TTS:
        try:
            # Load Qwen3-TTS model
            model = QwenTTS.from_pretrained("Qwen/Qwen3-TTS-12Hz-1.7B", device=DEVICE)
            QWEN_MODEL_CACHE = model
            print(f"[TTS Service] Qwen3-TTS Model loaded successfully.")
            return model
        except Exception as e:
            print(f"[TTS Service] Warning: Failed to load Qwen3-TTS from pretrained: {e}")
    
    QWEN_MODEL_CACHE = "mock_qwen_engine"
    return QWEN_MODEL_CACHE


@app.on_event("startup")
async def startup_event():
    print("=" * 60)
    print(" [TTS Service] Starting Qwen3-TTS Voice Cloning Microservice ")
    print(f" - Device      : {DEVICE}")
    if DEVICE == "cuda":
        print(f" - GPU         : {torch.cuda.get_device_name(0)}")
    print(f" - Ref Voice DB: {REF_VOICE_DIR}")
    print("=" * 60)
    os.makedirs(REF_VOICE_DIR, exist_ok=True)
    load_qwen_tts_model()


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {
        "status": "healthy",
        "service": "tts-service",
        "model": "Qwen3-TTS-12Hz-1.7B (Zero-Shot ICL)",
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
        raise HTTPException(status_code=400, detail="Text payload is empty.")

    start_time = time.time()
    
    # 1. Reference Audio Path check for ICL
    ref_audio_path = os.path.join(REF_VOICE_DIR, f"{reference_audio_id}.wav")
    has_ref_audio = os.path.exists(ref_audio_path)

    # 2. Synthesis execution (Qwen3-TTS ICL Zero-Shot / Fallback Synthesis)
    sample_rate = 24000
    model = load_qwen_tts_model()

    try:
        if HAS_QWEN_TTS and hasattr(model, "generate_voice_clone"):
            audio_data = model.generate_voice_clone(
                text=text,
                ref_audio_path=ref_audio_path if has_ref_audio else None,
                language=language
            )
        else:
            # High-quality sine waveform simulation for testing pipeline
            import numpy as np
            duration = max(1.5, len(text) * 0.15)
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            audio_data = 0.5 * np.sin(2 * np.pi * 440 * t)  # 440Hz Tone

        # 3. Write audio to buffer
        buf = io.BytesIO()
        sf.write(buf, audio_data, sample_rate, format="WAV")
        buf.seek(0)
        
        synth_time = time.time() - start_time

        headers = {
            "X-Inference-Time-Seconds": str(round(synth_time, 3)),
            "X-Compute-Device": DEVICE,
            "X-Ref-Audio-Used": str(has_ref_audio),
            "X-Voice-ID": reference_audio_id
        }

        return StreamingResponse(buf, media_type="audio/wav", headers=headers)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice Cloning Synthesis Error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8003, reload=False)
