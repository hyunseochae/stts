#!/usr/bin/env python3
"""
[Mac Live Microphone Real-time Test Client]
맥(macOS) 마이크를 이용해 실시간으로 음성을 녹음하고,
원격 STT/LLM/TTS 게이트웨이(ugai-sg.nb.is)로 전송 후,
합성되어 돌아온 응답 음성을 Mac 스피커로 직접 들어보는 테스트 스크립트
"""

import sys
import os
import time
import argparse
import subprocess
import wave
import requests
from urllib.parse import unquote

try:
    import sounddevice as sd
    import numpy as np
    HAS_SOUNDDEVICE = True
except ImportError:
    HAS_SOUNDDEVICE = False

DEFAULT_GATEWAY_URL = os.getenv("GATEWAY_URL", "http://ugai-sg.nb.is:8000")


def record_audio_mic(output_filename: str, duration: int = 4, sample_rate: int = 16000):
    print(f"\n🎙️  [마이크 녹음 시작] {duration}초간 음성을 말씀해 주세요...")
    print("   👉 예: '아이스 아메리카노 한 잔이랑 바닐라 라떼 한 잔 주세요.'")
    
    if HAS_SOUNDDEVICE:
        audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
        for i in range(duration, 0, -1):
            print(f"   ⏳ 녹음 남은 시간: {i}초...", end="\r", flush=True)
            time.sleep(1)
        sd.wait()
        print("\n✅  [마이크 녹음 완료] 오디오 서버로 전송 중...")
        
        with wave.open(output_filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio_data.tobytes())
    else:
        cmd = [
            "ffmpeg", "-y", "-f", "avfoundation", "-i", ":0",
            "-t", str(duration), "-ar", str(sample_rate), "-ac", "1", output_filename
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("\n✅  [마이크 녹음 완료] (ffmpeg 사용)")


def play_audio_file(audio_path: str):
    if os.path.exists(audio_path):
        print(f"\n🔊  [AI 음성 응답 스피커 재생 중...] ('{audio_path}')", flush=True)
        try:
            subprocess.run(["afplay", audio_path], check=True)
            print("✨  [재생 완료]\n", flush=True)
        except Exception as e:
            print(f"⚠️  음성 재생 중 오류 발생: {e}", flush=True)


def main():
    parser = argparse.ArgumentParser(description="Mac Interactive Voice Kiosk Test")
    parser.add_argument("--gateway", type=str, default=DEFAULT_GATEWAY_URL, help="Target Gateway URL")
    parser.add_argument("--duration", type=int, default=4, help="Microphone recording duration in seconds")
    parser.add_argument("--voice-id", type=str, default="default_owner", help="Reference voice ID for TTS cloning")
    args = parser.parse_args()

    print("=" * 65)
    print(" 🍎 [Mac Live Microphone Voice Kiosk Client] ")
    print(f" - Gateway Server : {args.gateway}")
    print(f" - Record Duration: {args.duration} 초")
    print("=" * 65)

    mic_file = "mac_mic_input.wav"
    output_file = "mac_received_voice.wav"

    input("\n엔터(Enter) 키를 누르면 마이크 녹음이 시작됩니다... ")
    
    # 1. 녹음 수행
    record_audio_mic(mic_file, duration=args.duration)

    # 2. 게이트웨이 전송
    chat_url = f"{args.gateway.rstrip('/')}/api/v1/assistant/chat"
    print(f"\n🚀 [서버로 음성 전송 중...] ({chat_url})", flush=True)

    start_time = time.time()
    try:
        with open(mic_file, "rb") as f:
            files = {"file": (os.path.basename(mic_file), f, "audio/wav")}
            data = {
                "reference_audio_id": args.voice_id,
                "language": "ko"
            }
            res = requests.post(chat_url, files=files, data=data, timeout=60)

        latency = time.time() - start_time

        if res.status_code == 200:
            raw_stt = res.headers.get('X-STT-User-Text', 'N/A')
            raw_resp = res.headers.get('X-LLM-Response-Text', 'N/A')
            stt_text = unquote(raw_stt) if raw_stt != 'N/A' else 'N/A'
            resp_text = unquote(raw_resp) if raw_resp != 'N/A' else 'N/A'

            print("\n" + "=" * 65, flush=True)
            print(" 🎉 [키오스크 음성 비서 수신 성공!] ", flush=True)
            print("=" * 65, flush=True)
            print(f" ⏱️ Total Latency        : {latency:.3f} 초", flush=True)
            print(f" 🎙️ 사용자 입력 STT 결과  : \"{stt_text}\"", flush=True)
            print(f" 🎯 LLM 파싱 의도        : {res.headers.get('X-LLM-Intent', 'N/A')}", flush=True)
            print(f" 🤖 AI 키오스크 답변     : \"{resp_text}\"", flush=True)
            print(f" ⚡ 서버 총 처리 시간    : {res.headers.get('X-Pipeline-Total-Time', 'N/A')} 초", flush=True)
            print("=" * 65, flush=True)

            with open(output_file, "wb") as out_f:
                out_f.write(res.content)
            print(f"\n💾 수신된 음성 파일 저장 완료: '{output_file}' ({len(res.content)} bytes)", flush=True)

            # 3. 스피커로 음성 재생
            play_audio_file(output_file)

        else:
            print(f"\n❌ 서버 응답 오류 (HTTP {res.status_code}): {res.text}", flush=True)

    except Exception as e:
        print(f"\n❌ 서버 통신 에러: {e}", flush=True)


if __name__ == "__main__":
    main()
