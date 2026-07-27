import os
import sys
import time
import tempfile
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import torch

try:
    from faster_whisper import WhisperModel
    HAS_FASTER_WHISPER = True
except ImportError:
    HAS_FASTER_WHISPER = False

import whisper

app = FastAPI(
    title="Whisper STT Microservice",
    description="FastAPI based Korean Speech-to-Text Container Service for Kiosk Systems",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_CACHE = {}
DEFAULT_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "base")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

class SegmentResult(BaseModel):
    start: float
    end: float
    text: str

class STTResponse(BaseModel):
    status: str
    text: str
    language: str
    inference_time_seconds: float
    compute_device: str
    segments: List[SegmentResult]

def get_whisper_model(model_size: str = DEFAULT_MODEL_SIZE):
    cache_key = f"{model_size}_{DEVICE}"
    if cache_key in MODEL_CACHE:
        return MODEL_CACHE[cache_key]

    print(f"[STT Service] Loading Whisper Model '{model_size}' on [{DEVICE}]...", flush=True)
    if HAS_FASTER_WHISPER:
        compute_type = "float16" if DEVICE == "cuda" else "int8"
        try:
            model = WhisperModel(model_size, device=DEVICE, compute_type=compute_type)
            MODEL_CACHE[cache_key] = ("faster", model)
            return ("faster", model)
        except Exception as e:
            print(f"[STT Service] Faster-Whisper init failed on {DEVICE}: {e}. Falling back to CPU/Official Whisper.", flush=True)

    try:
        model = whisper.load_model(model_size, device=DEVICE)
        MODEL_CACHE[cache_key] = ("openai", model)
        return ("openai", model)
    except Exception as e:
        print(f"[STT Service] OpenAI Whisper init failed on {DEVICE}: {e}. Retrying on CPU.", flush=True)
        model = whisper.load_model(model_size, device="cpu")
        MODEL_CACHE[cache_key] = ("openai_cpu", model)
        return ("openai_cpu", model)


@app.on_event("startup")
async def startup_event():
    print("=" * 60, flush=True)
    print(" [STT Service] Starting Whisper STT Microservice ", flush=True)
    print(f" - Device : {DEVICE}", flush=True)
    if DEVICE == "cuda":
        print(f" - GPU    : {torch.cuda.get_device_name(0)}", flush=True)
    print("=" * 60, flush=True)
    get_whisper_model(DEFAULT_MODEL_SIZE)


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {
        "status": "healthy",
        "service": "stt-service",
        "device": DEVICE,
        "gpu_available": torch.cuda.is_available(),
        "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None
    }


@app.post("/api/v1/stt", response_model=STTResponse)
async def transcribe_audio(
    file: UploadFile = File(...),
    language: str = Form("ko"),
    model_size: Optional[str] = Form(DEFAULT_MODEL_SIZE)
):
    if not file:
        raise HTTPException(status_code=400, detail="Audio file is required.")

    file_ext = os.path.splitext(file.filename)[1] or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    start_time = time.time()
    try:
        engine_type, model = get_whisper_model(model_size)
        segments_list = []
        full_text = []

        if engine_type == "faster":
            segments, info = model.transcribe(
                tmp_path,
                language=language,
                beam_size=5,
                vad_filter=True
            )
            for seg in segments:
                text = seg.text.strip()
                full_text.append(text)
                segments_list.append(SegmentResult(
                    start=round(seg.start, 2),
                    end=round(seg.end, 2),
                    text=text
                ))
            detected_lang = info.language
        else:
            target_device = "cpu" if engine_type == "openai_cpu" else DEVICE
            result = model.transcribe(
                tmp_path,
                language=language,
                fp16=(target_device == "cuda")
            )
            full_text.append(result["text"].strip())
            for seg in result.get("segments", []):
                segments_list.append(SegmentResult(
                    start=round(seg["start"], 2),
                    end=round(seg["end"], 2),
                    text=seg["text"].strip()
                ))
            detected_lang = language

        inference_time = time.time() - start_time
        final_text = " ".join(full_text).strip()

        print(f"\n[STT Service] 🎙️ Transcribed Audio -> Result STT Text: '{final_text}' (took {inference_time:.2f}s)", flush=True)

        return STTResponse(
            status="success",
            text=final_text,
            language=detected_lang,
            inference_time_seconds=round(inference_time, 3),
            compute_device=DEVICE if engine_type != "openai_cpu" else "cpu",
            segments=segments_list
        )

    except Exception as e:
        print(f"[STT Service Error] STT Exception: {e}", flush=True)
        raise HTTPException(status_code=500, detail=f"STT Processing Error: {str(e)}")

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8001, reload=False)
