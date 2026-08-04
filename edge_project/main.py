import time
import sys
import os
import argparse
import config
from audio.recorder import AudioRecorder
from audio.player import AudioPlayer
from stt.stt_engine import STTEngine
from llm.order_parser import LLMOrderParser
from tts.tts_engine import TTSEngine

def main():
    parser = argparse.ArgumentParser(description="Edge Kiosk Voice Assistant Pipeline")
    parser.add_argument("--file", type=str, default=None, help="테스트할 WAV 음성 파일 경로 (기본값: config.INPUT_AUDIO_PATH 사용 가능)")
    args = parser.parse_args()

    print("=" * 60)
    print("🤖 [Edge Kiosk Voice Assistant] 라즈베리파이 음성 안내 시스템")
    print("=" * 60)
    print(f"📋 [판매 메뉴 목록]: {', '.join(config.KIOSK_MENU)}")
    print("=" * 60)

    # 모듈 초기화
    recorder = AudioRecorder()
    player = AudioPlayer()
    stt = STTEngine()
    llm = LLMOrderParser()
    tts = TTSEngine()

    print("\n✅ 시스템이 준비되었습니다! (종료는 Ctrl+C)")

    # 명령줄 인자로 파일 지정되거나 실행 시 선택
    target_file_mode = args.file

    while True:
        try:
            audio_file = None

            if target_file_mode:
                audio_file = target_file_mode
                print(f"\n📂 [파일 테스트 모드] 입력 파일 사용: {audio_file}")
                input("👉 엔터(Enter) 키를 누르면 파이프라인(STT➔LLM➔TTS)을 실행합니다...")
            else:
                print("\n[모드 선택]")
                print(" 1. 🎙️ 실시간 마이크 녹음 모드")
                print(f" 2. 📂 저장된 WAV 파일 테스트 모드 ('{config.INPUT_AUDIO_PATH}')")
                mode = input("👉 모드를 선택하세요 (1 또는 2, 기본값: 1): ").strip()

                if mode == "2":
                    audio_file = config.INPUT_AUDIO_PATH
                    if not os.path.exists(audio_file):
                        print(f"❌ '{audio_file}' 파일이 존재하지 않습니다. 먼저 Mac에서 record_mac.py로 녹음해 주세요!")
                        continue
                else:
                    input("👉 엔터(Enter) 키를 누르면 마이크 녹음을 시작합니다...")
                    t0 = time.time()
                    audio_file = recorder.record_audio()
                    if not audio_file:
                        continue

            t0 = time.time()

            # Step 1: STT 음성 텍스트 변환
            t1 = time.time()
            user_text = stt.transcribe(audio_file)
            stt_latency = time.time() - t1

            if not user_text:
                print("⚠️ 인식된 음성 텍스트가 없습니다. 다시 시도해 주세요.")
                if target_file_mode:
                    break
                continue

            # Step 2: LLM 의도 파악 및 주문 JSON 추출
            t2 = time.time()
            result = llm.parse_order(user_text)
            llm_latency = time.time() - t2

            orders = result.get("orders", [])
            response_text = result.get("response_text", "")

            # 화면에 키오스크 장바구니 출력
            print("\n🛒 [키오스크 장바구니 결과]")
            if orders:
                for idx, item in enumerate(orders, 1):
                    print(f"   {idx}. {item['item']}: {item['quantity']}잔")
            else:
                print("   (선택된 상품 없음)")

            print(f"💬 [안내 멘트]: \"{response_text}\"")

            # Step 3: TTS 음성 합성 및 재생
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

            if target_file_mode:
                print("✅ 파일 테스트 완료.")
                break

        except KeyboardInterrupt:
            print("\n👋 키오스크 시스템을 종료합니다. 감사합니다.")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()
