#!/usr/bin/env python3
"""
Whisper (OpenAI Official) 한국어 STT 테스트 스크립트
(RTX 5090 / CUDA 지원 & CPU Fallback 포함)
"""

import sys
import os
import time
import argparse
import torch
import whisper


def run_stt(audio_path: str, model_name: str = "turbo", language: str = "ko", device: str = None):
    # 1. Device selection
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    
    print("=" * 60)
    print(f"[Whisper Official STT Test]")
    print(f" - Target Audio : {audio_path}")
    print(f" - Model Name   : {model_name}")
    print(f" - Language     : {language}")
    print(f" - Requested Dev: {device}")
    if device == "cuda" and torch.cuda.is_available():
        try:
            print(f" - GPU Device   : {torch.cuda.get_device_name(0)}")
        except Exception:
            pass
    print("=" * 60)

    if not os.path.exists(audio_path):
        print(f"Error: Audio file '{audio_path}' does not exist.")
        sys.exit(1)

    # 2. Model Load
    print(f"\n[1] Loading Whisper model '{model_name}' onto {device}...")
    start_load = time.time()
    try:
        model = whisper.load_model(model_name, device=device)
    except Exception as e:
        print(f"\n[Warning] Failed to load model on '{device}': {e}")
        if device == "cuda":
            print(" -> Retrying model load with CPU fallback...")
            device = "cpu"
            model = whisper.load_model(model_name, device=device)
        else:
            raise e

    load_time = time.time() - start_load
    print(f" -> Model loaded successfully on [{device}] in {load_time:.2f} seconds.")

    # 3. Transcribe
    print(f"\n[2] Transcribing audio '{audio_path}'...")
    start_transcribe = time.time()
    
    try:
        result = model.transcribe(
            audio_path,
            language=language,
            verbose=False,
            fp16=(device == "cuda")
        )
    except Exception as e:
        print(f"\n[Warning] Transcription failed on '{device}': {e}")
        if device == "cuda":
            print(" -> Retrying transcription on CPU...")
            device = "cpu"
            model = model.to("cpu")
            result = model.transcribe(
                audio_path,
                language=language,
                verbose=False,
                fp16=False
            )
        else:
            raise e

    transcribe_time = time.time() - start_transcribe
    print(f" -> Transcription finished in {transcribe_time:.2f} seconds.")

    # 4. Result Output
    print("\n" + "=" * 60)
    print(" [Transcription Result] ")
    print("=" * 60)
    print(result["text"].strip())
    print("=" * 60)

    # 5. Detailed Segment Breakdown
    print("\n[Detailed Segments with Timestamps]")
    for seg in result.get("segments", []):
        start = seg["start"]
        end = seg["end"]
        text = seg["text"].strip()
        print(f"[{start:06.2f}s -> {end:06.2f}s] {text}")

    print("\n[Summary]")
    print(f" - Final Compute Device : {device}")
    print(f" - Model Loading Time   : {load_time:.2f} s")
    print(f" - Inference Time        : {transcribe_time:.2f} s")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Whisper Korean STT Test Script (OpenAI Official)")
    parser.add_argument("--audio", type=str, default="sample_korean.wav", help="Path to input audio file (wav/mp3/flac)")
    parser.add_argument("--model", type=str, default="turbo", choices=["tiny", "base", "small", "medium", "large", "large-v3", "turbo"], help="Whisper model size")
    parser.add_argument("--language", type=str, default="ko", help="Language code (e.g. ko for Korean)")
    parser.add_argument("--device", type=str, default=None, choices=["cuda", "cpu"], help="Compute device")

    args = parser.parse_args()
    run_stt(audio_path=args.audio, model_name=args.model, language=args.language, device=args.device)
