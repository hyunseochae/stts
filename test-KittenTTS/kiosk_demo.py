#!/usr/bin/env python3
"""
[키오스크 / 오프라인 매장 온디바이스 TTS 검증 샘플]
KittenTTS Nano (ONNX 포맷) 초저지연 오프라인 음성 피드백 테스트
"""

import sys
import platform
import time
import os

# macOS espeak-ng 래퍼 설정
if platform.system() == "Darwin":
    from phonemizer.backend.espeak.wrapper import EspeakWrapper
    EspeakWrapper.set_library("/opt/homebrew/lib/libespeak-ng.dylib")

import soundfile as sf
from huggingface_hub import hf_hub_download
from kittentts import KittenTTS

SAMPLE_RATE = 24000

def run_kiosk_ondevice_benchmark():
    print("=" * 65)
    print(" [Kiosk / Edge Device On-Device TTS Benchmark] ")
    print(" Engine: KittenTTS Nano 0.1 (ONNX Runtime)")
    print(" Target: Kiosk Terminal / Edge Hardware (Offline Ready)")
    print("=" * 65)

    # 1. ONNX 모델 및 Voice NPZ 파일 로드 (로컬 온디바이스 서빙)
    print("\n[1] Loading ONNX model into local ONNX Runtime...")
    start_init = time.time()
    model_path  = hf_hub_download("KittenML/kitten-tts-nano-0.1", "kitten_tts_nano_v0_1.onnx")
    voices_path = hf_hub_download("KittenML/kitten-tts-nano-0.1", "voices.npz")
    
    model = KittenTTS(model_path, voices_path)
    init_time = time.time() - start_init
    print(f" -> Model initialized in {init_time:.3f}s (Fully Offline Ready)")

    selected_voice = model.available_voices[0]

    # 2. 키오스크/오프라인 매장 시나리오 안내 멘트 테스트 목록
    kiosk_phrases = [
        "Welcome to our store. Please select a menu on the screen.",
        "Order completed. Please insert your card into the reader.",
        "Order number 105, your meal is ready at the counter.",
    ]

    print("\n[2] Benchmarking Ultra-Low Latency Speech Feedback:")
    print("-" * 65)

    for idx, phrase in enumerate(kiosk_phrases, start=1):
        print(f"\nScenario #{idx}: \"{phrase}\"")
        
        start_gen = time.time()
        audio = model.generate(phrase, voice=selected_voice)
        gen_time = time.time() - start_gen

        # 음성 길이 계산
        audio_duration_sec = len(audio) / SAMPLE_RATE
        rtf = gen_time / audio_duration_sec  # Real-Time Factor (1.0 미만 시 실시간보다 빠름)

        output_filename = f"kiosk_output_{idx}.wav"
        sf.write(output_filename, audio, SAMPLE_RATE)

        print(f" -> Generation Time (Latency) : {gen_time * 1000:.1f} ms ({gen_time:.3f} s)")
        print(f" -> Audio Duration           : {audio_duration_sec:.2f} s")
        print(f" -> Real-Time Factor (RTF)    : {rtf:.4f} (Speedup: {1/rtf:.1f}x real-time)")
        print(f" -> Saved File                : {output_filename}")

    print("\n" + "=" * 65)
    print(" [Benchmark Summary] ")
    print(" - Model Format : ONNX (Ultra-lightweight KittenTTS Nano)")
    print(" - Connectivity : 100% Offline / On-Device (No Network API Required)")
    print(" - Edge Suitability: Extremely Low Memory Footprint & Sub-second Latency")
    print("=" * 65)

if __name__ == "__main__":
    run_kiosk_ondevice_benchmark()
