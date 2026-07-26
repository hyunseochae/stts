import torch
import soundfile as sf
import time
from qwen_tts import Qwen3TTSModel

# 1. 모델 로드 (RTX 5090의 VRAM을 활용하여 1.7B 모델 로드)
# device_map='cuda' 설정으로 GPU 가속을 사용합니다.
print("모델 로딩 중...")
model = Qwen3TTSModel.from_pretrained(
    "Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice",
    device_map="cuda",
    dtype=torch.bfloat16
    # flash-attn은 CUDA 라이브러리 호환성 문제로 비활성화
)
print("모델 로딩 완료!")

# 2. 한국어 텍스트 및 음성 설정
text = "안녕하세요. RTX 5090 서버에서 Qwen3 TTS를 이용해 한국어 음성을 생성하고 있습니다. 정말 빠르고 자연스럽네요!"

# 3. 음성 생성 (CustomVoice 모델은 사전 정의된 화자 선택 가능)
# 'Vivian' 등 한국어 톤에 맞는 화자를 지정하거나 설명을 추가할 수 있습니다.
print("음성 생성 중...")
start_time = time.time()
wavs, sample_rate = model.generate_custom_voice(
    text=text,
    speaker="Vivian",  # 기본 제공 화자 (Vivian, Serena 등)
    language="korean", # 한국어 설정 (지원: auto, chinese, english, french, german, italian, japanese, korean, portuguese, russian, spanish)
    instruct=None      # 선택사항: 감정 지시 (예: "용감한 목소리로 말해주세요")
)
generation_time = time.time() - start_time
print(f"⏱️  음성 생성 완료! 소요 시간: {generation_time:.2f}초")

# 4. 결과 저장
output_path = "output_korean.wav"
sf.write(output_path, wavs[0], sample_rate)
print(f"✅ 음성 파일이 성공적으로 생성되었습니다: {output_path}")
print(f"   샘플레이트: {sample_rate} Hz")
print(f"   오디오 길이: {len(wavs[0])/sample_rate:.2f}초")
