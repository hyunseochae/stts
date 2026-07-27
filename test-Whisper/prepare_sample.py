#!/usr/bin/env python3
"""
Whisper STT 테스트용 샘플 오디오 파일 준비 스크립트
"""

import os
import shutil
import sys


def prepare_sample():
    target_path = "sample_korean.wav"
    
    # 1. Check existing test audio from test-Qwen3-TTS
    source_candidates = [
        "../test-Qwen3-TTS/output_korean.wav",
        "../test-Qwen3-TTS/output_cloned_0.wav",
        "../test-KittenTTS/output.wav",
    ]

    found_source = None
    for src in source_candidates:
        abs_src = os.path.abspath(src)
        if os.path.exists(abs_src):
            found_source = abs_src
            break

    if found_source:
        print(f"Copying sample audio from '{found_source}' -> '{target_path}'...")
        shutil.copy(found_source, target_path)
        print("Sample audio prepared successfully.")
        return

    print(f"Notice: No existing sample audio found in parent folders.")
    print("Please place a Korean audio file (wav/mp3/flac) as 'sample_korean.wav' in this folder.")


if __name__ == "__main__":
    prepare_sample()
