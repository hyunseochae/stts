#!/usr/bin/env python3
"""
Faster-Whisper (CTranslate2) 한국어 STT 테스트 스크립트
고속 / 메모리 효율 최적화 Whisper 엔진 (GPU & CPU Fallback 지원)
"""

import sys
import os
import time
import argparse
import torch
from faster_whisper import WhisperModel


def run_stt(audio_path: str, model_size: str = "large-v3", language: str = "ko", device: str = None):
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    
    compute_type = "float16" if device == "cuda" else "int8"

    print("=" * 60)
    print(f"[Faster-Whisper STT Test]")
    print(f" - Target Audio : {audio_path}")
    print(f" - Model Size   : {model_size}")
    print(f" - Language     : {language}")
    print(f" - Requested Dev: {device} ({compute_type})")
    print("=" * 60)

    if not os.path.exists(audio_path):
        print(f"Error: Audio file '{audio_path}' does not exist.")
        sys.exit(1)

    # 1. Model Load with Fallback
    print(f"\n[1] Loading Faster-Whisper model '{model_size}'...")
    start_load = time.time()
    try:
        model = WhisperModel(model_size, device=device, compute_type=compute_type)
    except Exception as e:
        print(f"\n[Warning] Failed to initialize Faster-Whisper on '{device}': {e}")
        if device == "cuda":
            print(" -> Retrying model load with CPU (int8)...")
            device = "cpu"
            compute_type = "int8"
            model = WhisperModel(model_size, device=device, compute_type=compute_type)
        else:
            raise e

    load_time = time.time() - start_load
    print(f" -> Model loaded in {load_time:.2f} seconds on [{device}].")

    # 2. Transcribe
    print(f"\n[2] Transcribing audio '{audio_path}'...")
    start_transcribe = time.time()
    
    try:
        segments, info = model.transcribe(
            audio_path,
            language=language,
            beam_size=5,
            vad_filter=True
        )
        segment_list = []
        full_text = []
        for segment in segments:
            text = segment.text.strip()
            full_text.append(text)
            segment_list.append((segment.start, segment.end, text))
    except Exception as e:
        print(f"\n[Warning] Transcription failed on '{device}': {e}")
        if device == "cuda":
            print(" -> Retrying transcription on CPU...")
            device = "cpu"
            compute_type = "int8"
            model = WhisperModel(model_size, device=device, compute_type=compute_type)
            segments, info = model.transcribe(
                audio_path,
                language=language,
                beam_size=5,
                vad_filter=True
            )
            segment_list = []
            full_text = []
            for segment in segments:
                text = segment.text.strip()
                full_text.append(text)
                segment_list.append((segment.start, segment.end, text))
        else:
            raise e

    transcribe_time = time.time() - start_transcribe
    print(f" -> Transcription finished in {transcribe_time:.2f} seconds.")

    # 3. Output
    print("\n" + "=" * 60)
    print(" [Transcription Result] ")
    print("=" * 60)
    print(" ".join(full_text))
    print("=" * 60)

    print("\n[Detailed Segments with Timestamps]")
    for start, end, text in segment_list:
        print(f"[{start:06.2f}s -> {end:06.2f}s] {text}")

    print("\n[Summary]")
    print(f" - Final Compute Device : {device} ({compute_type})")
    print(f" - Model Loading Time   : {load_time:.2f} s")
    print(f" - Inference Time        : {transcribe_time:.2f} s")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Faster-Whisper Korean STT Test Script")
    parser.add_argument("--audio", type=str, default="sample_korean.wav", help="Path to input audio file")
    parser.add_argument("--model", type=str, default="large-v3", help="Model size (tiny, base, small, medium, large-v3, etc.)")
    parser.add_argument("--language", type=str, default="ko", help="Language code")
    parser.add_argument("--device", type=str, default=None, choices=["cuda", "cpu"], help="Compute device")

    args = parser.parse_args()
    run_stt(audio_path=args.audio, model_size=args.model, language=args.language, device=args.device)
