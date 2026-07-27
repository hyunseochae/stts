#!/usr/bin/env python3
"""
STT Microservice Direct Functional Verification Script
"""

import sys
import os
import time
import subprocess
import requests

def test_stt():
    print("=" * 60)
    print(" [STT Service] Starting Local API Test ")
    print("=" * 60)

    # 1. Check audio sample
    audio_sample = "../test-Whisper/sample_korean.wav"
    if not os.path.exists(audio_sample):
        audio_sample = "../../test-Qwen3-TTS/output_korean.wav"

    print(f" -> Using audio sample: {audio_sample}")

    # Start app.py via uvicorn in background
    venv_python = "../.venv/bin/python"
    env = os.environ.copy()
    
    server_process = subprocess.Popen(
        [venv_python, "-m", "uvicorn", "app:app", "--host", "127.0.0.1", "--port", "8001"],
        cwd=".",
        env=env
    )

    try:
        # Wait for server startup
        print(" -> Waiting for STT FastAPI server to initialize...")
        healthy = False
        for _ in range(15):
            time.sleep(1)
            try:
                r = requests.get("http://127.0.0.1:8001/health", timeout=2)
                if r.status_code == 200:
                    print(f" -> Healthcheck Success: {r.json()}")
                    healthy = True
                    break
            except Exception:
                pass

        if not healthy:
            print("Error: STT FastAPI server failed to start within timeout.")
            sys.exit(1)

        # 2. Test STT API (/api/v1/stt)
        print("\n -> Sending STT Request to POST /api/v1/stt...")
        with open(audio_sample, "rb") as f:
            files = {"file": ("sample.wav", f, "audio/wav")}
            data = {"language": "ko", "model_size": "tiny"}
            res = requests.post("http://127.0.0.1:8001/api/v1/stt", files=files, data=data, timeout=30)

        print("\n [STT API Response Output] ")
        print("-" * 60)
        print(f"Status Code: {res.status_code}")
        response_json = res.json()
        print(response_json)
        print("-" * 60)

        assert res.status_code == 200
        assert response_json["status"] == "success"
        assert len(response_json["text"]) > 0
        print("\n✅ STT Microservice Verification PASSED!")

    finally:
        print(" -> Terminating STT FastAPI server...")
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    test_stt()
