# Whisper 한국어 STT (Speech-to-Text) 테스트 환경

NVIDIA GPU (RTX 5090 등) 및 CPU 환경에서 Whisper 모델을 이용하여 한국어 음성 인식을 진행하기 위한 파이썬 테스트 환경입니다.

---

## 📁 디렉토리 구조

```
test-Whisper/
├── WANT.md                  # 작업 요구사항
├── 01-install.sh            # 가상환경 생성 및 의존성 설치 스크립트
├── requirements.txt         # Python 패키지 목록
├── prepare_sample.py        # 테스트용 샘플 오디오 복사/준비 스크립트
├── test-whisper-openai.py   # OpenAI 공식 Whisper 테스트 스크립트
├── test-whisper-faster.py   # Faster-Whisper (CTranslate2 최적화) 테스트 스크립트
├── sample_korean.wav        # (자동생성) 테스트용 한국어 음성 파일
└── README.md                # 사용 설명서
```

---

## ⚙️ 1. 테스트 환경 설치

아래 명령어를 통해 가상환경(`.venv`)을 작성하고 필요한 라이브러리(PyTorch CUDA, Whisper, Faster-Whisper 등)를 자동 설치합니다.

```bash
chmod +x 01-install.sh
./01-install.sh
```

설치 완료 후 가상환경을 활성화합니다:

```bash
source .venv/bin/activate
```

---

## 🎵 2. 샘플 오디오 준비

테스트할 음성 파일(`sample_korean.wav`)을 준비하거나 아래 스크립트로 기존 테스트 음성을 복사해 올 수 있습니다.

```bash
python prepare_sample.py
```

---

## 🧪 3. STT 테스트 실행

### Option A. OpenAI 공식 Whisper 테스트 (`test-whisper-openai.py`)

```bash
# 기본 실행 (turbo 모델, 한국어 자동 적용)
python test-whisper-openai.py --audio sample_korean.wav --model turbo

# 모델 크기 지정 (large-v3, medium, small, base 등)
python test-whisper-openai.py --audio sample_korean.wav --model large-v3
```

### Option B. Faster-Whisper 테스트 (`test-whisper-faster.py`)
CTranslate2 엔진 기반으로 GPU 메모리 사용량을 크게 줄이고 추론 속도를 대폭 향상시킨 버전입니다.

```bash
# 기본 실행 (large-v3 모델)
python test-whisper-faster.py --audio sample_korean.wav --model large-v3

# 타겟 오디오 지정
python test-whisper-faster.py --audio /path/to/your/audio.wav
```

---

## 💡 주요 특징 및 옵션 안내

- **GPU 자동 감지**: CUDA 구동 가능 시 GPU (`cuda`, FP16) 사용, 부재 시 자동 CPU (`cpu`, FP32/INT8)로 전환됩니다.
- **한국어 지정 (`language='ko'`)**: 한국어 음성에 맞게 타겟 언어를 지정하여 인식률을 극대화합니다.
- **타임스탬프 세그먼트**: 각 문장/구절별 시작 및 종료 시간과 인식 결과를 함께 제공합니다.
