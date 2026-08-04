#!/usr/bin/env python3
import time
import os
import sys

# edge_project 상위 폴더 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config
from audio.recorder import AudioRecorder

def main():
    print("=" * 60)
    print("🎙️ [Mac 마이크 음성 샘플 녹음기]")
    print("라즈베리파이 테스트용 'temp/input.wav' 음성 파일 생성 프로그램")
    print("=" * 60)
    print(f"📁 저장 위치: {config.INPUT_AUDIO_PATH}")
    print("=" * 60)

    recorder = AudioRecorder()
    input("\n👉 엔터(Enter) 키를 누르고 Mac 마이크에 주문 음성을 말씀하세요 (예: '아이스 아메리카노 2잔 주세요')...")

    audio_file = recorder.record_audio()

    if audio_file and os.path.exists(audio_file):
        size_kb = os.path.getsize(audio_file) / 1024
        print(f"\n🎉 성공적으로 녹음되었습니다!")
        print(f"   - 파일 경로: {audio_file}")
        print(f"   - 파일 용량: {size_kb:.1f} KB")
        print("\n💡 이제 이 'temp/input.wav' 파일 또는 Git을 통해 라즈베리파이로 복사하여 테스트하실 수 있습니다!")
    else:
        print("\n❌ 녹음에 실패했습니다. 마이크 접근 권한을 확인해 주세요.")

if __name__ == "__main__":
    main()
