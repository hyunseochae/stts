import torch
import torchaudio
import datetime
from chatterbox import ChatterboxMultilingualTTS

# RTX 5090 (sm_120) 지원을 위해 PyTorch 2.7.0+cu128을 사용합니다.
device = "cuda" if torch.cuda.is_available() else "cpu"

# 모델 로드 (한국어 포함 다국어 모델)
# from_pretrained는 내부적으로 "ResembleAI/chatterbox" 모델을 사용합니다.
model = ChatterboxMultilingualTTS.from_pretrained(device=device)

# 한국어 텍스트 입력 및 음성 생성
for i in range(3):
    ts_start = datetime.datetime.now()
    text = f"반갑습니다. {i+1}번째 작업, 알티엑스 오공구공 에서 채터박스 한국어 음성 합성을 시작합니다."
    audio = model.generate(
        text=text,
        language_id="ko",  # 한국어 설정
    )
    # 파일 저장 (torch.Tensor를 wav 파일로 저장)
    # model.sr은 모델의 샘플 레이트(24000)입니다.
    torchaudio.save(f"output_5090_{i+1}.wav", audio.cpu(), sample_rate=model.sr)

    ts_end = datetime.datetime.now()
    print(f"{i+1}번째 작업, 알티엑스 5090에서 채터박스 한국어 음성 합성 완료, 소요시간: {ts_end - ts_start}")

