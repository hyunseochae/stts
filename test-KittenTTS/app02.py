import sys
import platform
import time

# macOS에서 Homebrew로 설치된 espeak-ng 라이브러리 경로를 명시적으로 설정
# (ctypes.util.find_library가 /opt/homebrew/lib 경로를 자동으로 찾지 못하는 문제 우회)
if platform.system() == "Darwin":
    from phonemizer.backend.espeak.wrapper import EspeakWrapper
    EspeakWrapper.set_library("/opt/homebrew/lib/libespeak-ng.dylib")

import soundfile as sf
from huggingface_hub import hf_hub_download
from kittentts import KittenTTS

# KittenTTS 샘플레이트 (Kokoro 기반: 24000Hz)
SAMPLE_RATE = 24000

# HuggingFace에서 모델과 보이스 파일 다운로드 (캐시되므로 두 번째부터는 빠름)
print("모델 다운로드 중...")
model_path  = hf_hub_download("KittenML/kitten-tts-nano-0.1", "kitten_tts_nano_v0_1.onnx")
voices_path = hf_hub_download("KittenML/kitten-tts-nano-0.1", "voices.npz")
print(f"모델 경로: {model_path}")

# KittenTTS 초기화
model = KittenTTS(model_path, voices_path)

# 사용 가능한 보이스 목록 출력
print("사용 가능한 보이스:", model.available_voices)

text = """Game of Thrones is a sweeping fantasy drama set in Westeros, where noble families compete for the Iron Throne. Filled with political intrigue, shocking betrayals, dragons, and epic battles, the series explores power, loyalty, and survival. Complex characters and unpredictable twists made it a global television phenomenon.
"""

# 보이스 선택 (available_voices 목록에서 첫 번째 사용)
selected_voice = model.available_voices[0]
print(f"선택된 보이스: {selected_voice}")

# 오디오 생성 시작 시각 기록
start_time = time.time()
print(f"[시작] {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}")

audio = model.generate(
    text,
    voice=selected_voice
)

# 출력 저장 (soundfile로 올바른 WAV 헤더 포함 저장)
sf.write("output.wav", audio, SAMPLE_RATE)

# 오디오 생성 종료 시각 및 소요 시간 기록
end_time = time.time()
print(f"[종료] {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))}")
print(f"[소요] {end_time - start_time:.3f}초")

print("오디오 생성 완료! output.wav 저장됨")
