import torch
import soundfile as sf
import time
from qwen_tts import Qwen3TTSModel

# 1. Base 모델 로드 (보이스 클로닝을 위해 Base 모델 사용)
# device_map='cuda' 설정으로 GPU 가속을 사용합니다.
print("Base 모델 로딩 중...")
model = Qwen3TTSModel.from_pretrained(
    "Qwen/Qwen3-TTS-12Hz-1.7B-Base",  # Base 모델 (보이스 클로닝 지원)
    device_map="cuda",
    dtype=torch.bfloat16
    # flash-attn은 CUDA 라이브러리 호환성 문제로 비활성화
)
print("모델 로딩 완료!")

# 2. 참조 오디오 및 텍스트 설정
# TODO: 실제 참조 오디오 파일 경로로 변경하세요
ref_audio_path = "ref02.mp3"  # 클로닝할 음성 샘플 파일
ref_text = "이것은 참조 오디오의 텍스트입니다."  # 참조 오디오에서 말하는 내용

# 생성할 텍스트
text = "안녕하세요. RTX 5090 서버에서 Qwen3 TTS를 이용해 보이스 클로닝을 하고 있습니다. 정말 놀라운 기술이네요!"

# 3. 보이스 클로닝으로 음성 생성
print("보이스 클로닝 중...")
start_time = time.time()
wavs, sample_rate = model.generate_voice_clone(
    text=text,
    language="korean",  # 한국어 설정
    ref_audio=ref_audio_path,  # 참조 오디오 파일 경로
    ref_text=ref_text,  # 참조 오디오의 텍스트 (ICL 모드에서 필요)
    x_vector_only_mode=False  # False: ICL 모드 (더 좋은 품질), True: x-vector만 사용 (빠르지만 품질 낮음)
)
generation_time = time.time() - start_time
print(f"⏱️  보이스 클로닝 완료! 소요 시간: {generation_time:.2f}초")

# 4. 결과 저장
output_path = "output_cloned.wav"
sf.write(output_path, wavs[0], sample_rate)
print(f"✅ 클로닝된 음성 파일이 성공적으로 생성되었습니다: {output_path}")
print(f"   샘플레이트: {sample_rate} Hz")
print(f"   오디오 길이: {len(wavs[0])/sample_rate:.2f}초")

