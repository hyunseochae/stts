#!/usr/bin/env python3
"""
[Kiosk Edge Terminal Test Client]
키오스크 엣지 단말기에서 원격 백엔드 MSA (API Gateway)로
음성을 전송하고 응답 음성을 받아 재생/저장하는 시뮬레이션 클라이언트
"""

import sys
import os
import time
import argparse
import requests

# Remote Gateway Default Host
DEFAULT_GATEWAY_URL = os.getenv("GATEWAY_URL", "http://ugai-sg.nb.is:8000")


def run_kiosk_edge_test(audio_path: str, gateway_url: str, reference_voice_id: str):
    print("=" * 65)
    print(" [Kiosk Edge Terminal Simulation Client] ")
    print(f" - Target Server Gateway : {gateway_url}")
    print(f" - Input Audio Payload   : {audio_path}")
    print(f" - Reference Voice ID    : {reference_voice_id}")
    print("=" * 65)

    if not os.path.exists(audio_path):
        print(f"Error: Target audio file '{audio_path}' does not exist.")
        sys.exit(1)

    # 1. Gateway Health check
    health_url = f"{gateway_url.rstrip('/')}/health"
    print(f"\n[1] Connecting to Remote Server Gateway ({health_url})...")
    try:
        r = requests.get(health_url, timeout=5)
        print(f" -> Gateway Connection Status : HTTP {r.status_code}")
        print(f" -> Service Health Details    : {r.json()}")
    except Exception as e:
        print(f"[Warning] Gateway healthcheck failed: {e}")
        print(" -> Attempting direct pipeline request...")

    # 2. Send Audio Command & Process E2E Pipeline
    chat_url = f"{gateway_url.rstrip('/')}/api/v1/assistant/chat"
    print(f"\n[2] Sending Audio Stream to Kiosk Voice Assistant ({chat_url})...")

    start_time = time.time()
    try:
        with open(audio_path, "rb") as f:
            files = {"file": (os.path.basename(audio_path), f, "audio/wav")}
            data = {
                "reference_audio_id": reference_voice_id,
                "language": "ko"
            }
            res = requests.post(chat_url, files=files, data=data, timeout=60)

        latency = time.time() - start_time

        print("\n" + "=" * 65)
        print(" [Kiosk Edge Terminal Response Received] ")
        print("=" * 65)
        print(f" -> Response Status Code     : HTTP {res.status_code}")
        print(f" -> Total Roundtrip Latency  : {latency:.3f} seconds")
        print(f" -> Recognized STT Text      : {res.headers.get('X-STT-User-Text', 'N/A')}")
        print(f" -> Recognized LLM Intent    : {res.headers.get('X-LLM-Intent', 'N/A')}")
        print(f" -> Generated Response Text  : {res.headers.get('X-LLM-Response-Text', 'N/A')}")
        print(f" -> Server Processing Time   : {res.headers.get('X-Pipeline-Total-Time', 'N/A')} s")
        print("=" * 65)

        if res.status_code == 200:
            output_file = "edge_received_voice.wav"
            with open(output_file, "wb") as out_f:
                out_f.write(res.content)
            print(f"\n✅ Received Cloned Audio saved successfully as '{output_file}' ({len(res.content)} bytes)")
        else:
            print(f"\n❌ Error Response from Server: {res.text}")

    except Exception as e:
        print(f"\n❌ Connection Error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kiosk Edge Client Test Script")
    parser.add_argument("--audio", type=str, default="../../test-Whisper/sample_korean.wav", help="Path to input audio file")
    parser.add_argument("--gateway", type=str, default=DEFAULT_GATEWAY_URL, help="Target Gateway URL")
    parser.add_argument("--voice-id", type=str, default="default_owner", help="Reference voice ID for cloning")

    args = parser.parse_args()
    
    # Fallback audio path check
    if not os.path.exists(args.audio):
        fallback_path = "../../test-Qwen3-TTS/output_korean.wav"
        if os.path.exists(fallback_path):
            args.audio = fallback_path

    run_kiosk_edge_test(audio_path=args.audio, gateway_url=args.gateway, reference_voice_id=args.voice_id)
