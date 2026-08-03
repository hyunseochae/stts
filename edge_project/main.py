import time
import sys
import config
from audio.recorder import AudioRecorder
from audio.player import AudioPlayer
from stt.stt_engine import STTEngine
from llm.order_parser import LLMOrderParser
from tts.tts_engine import TTSEngine

def main():
    print("=" * 60)
    print("🤖 [Edge Kiosk Voice Assistant] 라즈베리파이 음성 안내 시스템")
    print("=" * 60)
    print(f"📋 [판매 메뉴 목록]: {', '.join(config.KIOSK_MENU)}")
    print("=" * 60)

    # 1. 각 엔진 및 오디오 모듈 초기화
    recorder = AudioRecorder()
    player = AudioPlayer()
    stt = STTEngine()
    llm = LLMOrderParser()
    tts = TTSEngine()

    print("\n✅ 시스템이 준비되었습니다! 팟(Pod) 주문을 시작합니다. (종료는 Ctrl+C)")

    while True:
        try:
            input("\n👉 엔터(Enter) 키를 누르면 음성 주문 녹음을 시작합니다...")

            # Step 1: 음성 녹음
            t0 = time.time()
            audio_file = recorder.record_audio()
            if not audio_file:
                continue

            # Step 2: STT 음성 텍스트 변환
            t1 = time.time()
            user_text = stt.transcribe(audio_file)
            stt_latency = time.time() - t1

            if not user_text:
                print("⚠️ 인식된 음성 텍스트가 없습니다. 다시 시도해 주세요.")
                continue

            # Step 3: LLM 의도 파악 및 주문 JSON 추출
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

            # Step 4: TTS 음성 합성 및 재생
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
            print("\n👋 키오스크 시스템을 종료합니다. 감사합니다.")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()
