#!/usr/bin/env python3
"""
Mac 전용 로컬 실시간 음성 키오스크 인터랙티브 테스트 프로그램 (testinlocal)
Mac 마이크로 직접 말하고 Mac 스피커로 안내 음성을 듣는 전용 테스트 스크립트입니다.
"""

import os
import sys
import time

# edge_project 디렉터리를 모듈 경로에 추가하여 엔진 재사용
EDGE_PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "edge_project"))
sys.path.append(EDGE_PROJECT_DIR)

import config
from audio.recorder import AudioRecorder
from audio.player import AudioPlayer
from stt.stt_engine import STTEngine
from llm.order_parser import LLMOrderParser
from tts.tts_engine import TTSEngine

def main():
    print("=" * 60)
    print("🖥️ [Mac 로컬 전용 실시간 음성 키오스크 테스트]")
    print("Mac 내장 마이크 ➔ STT ➔ LLM 주문 파싱 ➔ TTS ➔ Mac 스피커 재생")
    print("=" * 60)
    print(f"📋 [판매 메뉴 목록]: {', '.join(config.KIOSK_MENU)}")
    print("=" * 60)

    recorder = AudioRecorder()
    player = AudioPlayer()
    stt = STTEngine()
    llm = LLMOrderParser()
    tts = TTSEngine()

    print("\n✅ Mac 로컬 환경이 성공적으로 초기화되었습니다! (종료: Ctrl+C)")

    while True:
        try:
            input("\n👉 엔터(Enter) 키를 누르고 Mac 마이크에 음성 주문을 말씀하세요...")

            # 1. Mac 마이크 실시간 녹음
            t0 = time.time()
            audio_file = recorder.record_audio()
            if not audio_file:
                continue

            # 2. STT 음성 인식 (faster-whisper)
            t1 = time.time()
            user_text = stt.transcribe(audio_file)
            stt_latency = time.time() - t1

            if not user_text:
                print("⚠️ 인식된 음성 텍스트가 없습니다. 다시 시도해 주세요.")
                continue

            # 3. LLM 의도 파악 및 주문 JSON 추출 (오타 자동 교정 적용)
            t2 = time.time()
            result = llm.parse_order(user_text)
            llm_latency = time.time() - t2

            orders = result.get("orders", [])
            response_text = result.get("response_text", "")

            # 터미널에 키오스크 장바구니 결과 출력
            print("\n🛒 [키오스크 장바구니 결과]")
            if orders:
                for idx, item in enumerate(orders, 1):
                    print(f"   {idx}. {item['item']}: {item['quantity']}잔")
            else:
                print("   (선택된 상품 없음)")

            print(f"💬 [안내 멘트]: \"{response_text}\"")

            # 4. TTS 음성 합성 및 Mac 스피커 재생 (afplay)
            t3 = time.time()
            tts_file = tts.generate_speech(response_text)
            tts_latency = time.time() - t3

            if tts_file:
                player.play_audio(tts_file)

            total_latency = time.time() - t0
            print(f"\n⏱️ [파이프라인 소요 시간 측정]")
            print(f"   - STT 지연시간: {stt_latency:.2f}초")
            print(f"   - LLM 지연시간: {llm_latency:.2f}초")
            print(f"   - TTS 지연시간: {tts_latency:.2f}초")
            print(f"   - 전체 처리시간: {total_latency:.2f}초")
            print("-" * 60)

        except KeyboardInterrupt:
            print("\n👋 Mac 로컬 테스트 프로그램을 종료합니다.")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()
