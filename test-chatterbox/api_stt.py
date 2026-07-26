
import os
import shutil
import tempfile
from typing import Optional

import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException
from faster_whisper import WhisperModel

app = FastAPI(title="Chatterbox STT Service")

# 모델 로드 (전역 변수로 유지)
# Docker 환경변수 또는 기본값 사용
MODEL_SIZE = os.getenv("WHISPER_MODEL", "large-v3")
DEVICE = "cuda" if os.getenv("CUDA_VISIBLE_DEVICES") else "cpu"
COMPUTE_TYPE = "float16" if DEVICE == "cuda" else "int8"

print(f"Loading Whisper model: {MODEL_SIZE} on {DEVICE} with {COMPUTE_TYPE}...")
model = WhisperModel(MODEL_SIZE, device=DEVICE, compute_type=COMPUTE_TYPE)
print("Model loaded successfully.")

@app.post("/transcribe")
async def transcribe(
    file: UploadFile = File(...),
    language: Optional[str] = None,
    beam_size: int = 5
):
    """
    오디오 파일을 받아서 텍스트로 변환합니다.
    """
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")

    # 임시 파일로 저장
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.split('.')[-1]}") as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        temp_path = temp_file.name

    try:
        segments, info = model.transcribe(
            temp_path, 
            beam_size=beam_size, 
            language=language
        )
        
        # Generator를 리스트로 변환하여 전체 텍스트 합치기
        result_text = ""
        segments_list = []
        for segment in segments:
            segments_list.append({
                "start": segment.start,
                "end": segment.end,
                "text": segment.text
            })
            result_text += segment.text + " "

        return {
            "transcription": result_text.strip(),
            "language": info.language,
            "language_probability": info.language_probability,
            "segments": segments_list
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # 임시 파일 삭제
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.get("/health")
def health_check():
    return {"status": "ok", "model": MODEL_SIZE, "device": DEVICE}

if __name__ == "__main__":
    uvicorn.run("api_stt:app", host="0.0.0.0", port=8000, reload=False)
