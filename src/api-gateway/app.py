import os
import time
import httpx
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

STT_SERVICE_URL = os.getenv("STT_SERVICE_URL", "http://stts-stt-service:8001")
LLM_SERVICE_URL = os.getenv("LLM_SERVICE_URL", "http://stts-llm-service:8002")
TTS_SERVICE_URL = os.getenv("TTS_SERVICE_URL", "http://stts-tts-service:8003")

app = FastAPI(
    title="Voice Assistant API Gateway",
    description="Orchestrator Gateway for STT -> LLM -> TTS Modular Pipeline",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    health_results = {"gateway": "healthy", "services": {}}
    async with httpx.AsyncClient(timeout=3.0) as client:
        for name, url in [("stt", STT_SERVICE_URL), ("llm", LLM_SERVICE_URL), ("tts", TTS_SERVICE_URL)]:
            try:
                res = await client.get(f"{url}/health")
                health_results["services"][name] = res.json() if res.status_code == 200 else "unhealthy"
            except Exception as e:
                health_results["services"][name] = f"error: {str(e)}"
    return health_results


@app.post("/api/v1/assistant/chat")
async def process_full_voice_assistant_pipeline(
    file: UploadFile = File(...),
    reference_audio_id: str = Form("default_owner"),
    language: str = Form("ko")
):
    """
    End-to-End Pipeline:
    1. Audio File -> STT Service (STT Text)
    2. STT Text -> LLM Service (Intent & Response Text)
    3. Response Text -> TTS Service (Cloned Voice WAV Stream)
    """
    start_pipeline = time.time()
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Step 1: STT Request
        file_bytes = await file.read()
        files = {"file": (file.filename or "audio.wav", file_bytes, file.content_type or "audio/wav")}
        data = {"language": language}

        try:
            stt_res = await client.post(f"{STT_SERVICE_URL}/api/v1/stt", files=files, data=data)
            stt_data = stt_res.json()
            if stt_res.status_code != 200 or stt_data.get("status") != "success":
                raise HTTPException(status_code=500, detail=f"STT Service Error: {stt_data}")
            user_text = stt_data["text"]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to communicate with STT Service: {e}")

        # Step 2: LLM Intent Request
        try:
            llm_res = await client.post(f"{LLM_SERVICE_URL}/api/v1/intent", json={"user_text": user_text})
            llm_data = llm_res.json()
            if llm_res.status_code != 200 or llm_data.get("status") != "success":
                raise HTTPException(status_code=500, detail=f"LLM Service Error: {llm_data}")
            response_text = llm_data["response_text"]
            intent = llm_data["intent"]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to communicate with LLM Service: {e}")

        # Step 3: TTS Voice Cloning Request (JSON Body)
        try:
            tts_data = {
                "text": response_text,
                "reference_audio_id": reference_audio_id,
                "language": language
            }
            tts_res = await client.post(f"{TTS_SERVICE_URL}/api/v1/tts/clone", json=tts_data)
            if tts_res.status_code != 200:
                raise HTTPException(status_code=500, detail="TTS Service synthesis failed.")
            
            audio_bytes = tts_res.content
            total_pipeline_time = time.time() - start_pipeline

            from urllib.parse import quote
            headers = {
                "X-Pipeline-Total-Time": str(round(total_pipeline_time, 3)),
                "X-STT-User-Text": quote(user_text),
                "X-LLM-Intent": intent,
                "X-LLM-Response-Text": quote(response_text)
            }

            from fastapi.responses import Response
            return Response(
                content=audio_bytes,
                media_type="audio/wav",
                headers=headers
            )
        except HTTPException:
            raise
        except Exception as e:
            import traceback
            print(f"[API Gateway Error] TTS Step Exception: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Failed to communicate with TTS Service: {type(e).__name__} - {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)
