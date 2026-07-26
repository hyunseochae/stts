# RTX 5090 STT & TTS 테스트 결과 정리 (RTX 5090 STT & TTS Test Summary)

이 디렉토리는 **NVIDIA GeForce RTX 5090 GPU (Blackwell 아키텍처, CUDA 12.8/13.0 호환)** 환경에서 STT(Speech-to-Text) 및 TTS(Text-to-Speech) 모델들의 구동 및 성능을 테스트한 결과물들을 정리해 둔 곳입니다.

---

## 📂 테스트 프로젝트 구성 개요

현재 이 폴더는 아래와 같이 3가지 주요 STT/TTS 오픈소스 엔진을 대상으로 테스트를 진행했습니다.

| 디렉토리 명 | 테스트 구분 | 사용 모델 / 프레임워크 | 특징 / 목적 |
| :--- | :--- | :--- | :--- |
| [**`test-KittenTTS`**](file:///home/toor/IsItAI/test-STTS/test-KittenTTS) | **TTS** | `KittenML/kitten-tts-nano-0.1` (Kokoro ONNX) | 초경량 영어 음성 합성 (24kHz 샘플레이트) |
| [**`test-Qwen3-TTS`**](file:///home/toor/IsItAI/test-STTS/test-Qwen3-TTS) | **TTS** (한국어 & 보이스 클로닝) | `Qwen/Qwen3-TTS-12Hz-1.7B` (CustomVoice & Base) | RTX 5090 GPU 가속 (BF16), 한국어 고품질 음성 합성 및 Zero-shot 보이스 클로닝 |
| [**`test-chatterbox`**](file:///home/toor/IsItAI/test-STTS/test-chatterbox) | **TTS & STT** | `ResembleAI/chatterbox` & `faster-whisper` (large-v3) | 다국어 고속 TTS 및 FastAPI 기반 STT 컨테이너 서비스 구축 테스트 |

---

## 1. 🐱 [test-KittenTTS](file:///home/toor/IsItAI/test-STTS/test-KittenTTS)
* **목적**: ONNX 기반 초경량 TTS 엔진인 KittenTTS 구동 및 영어 텍스트 음성 합성 테스트
* **개발 및 실행 환경**:
  - Python `3.12` 가상환경 (`uv venv`)
  - 핵심 의존성: `kittentts`, `phonemizer` (Darwin 플랫폼 대응을 위해 `libespeak-ng.dylib` 경로 패치 포함)
* **주요 스크립트**:
  - [`01-install.sh`](file:///home/toor/IsItAI/test-STTS/test-KittenTTS/01-install.sh): `uv` 기반 3.12 가상환경 생성 및 git 레포를 통한 `KittenTTS` 패키지 설치
  - [`app01.py`](file:///home/toor/IsItAI/test-STTS/test-KittenTTS/app01.py) & [`app02.py`](file:///home/toor/IsItAI/test-STTS/test-KittenTTS/app02.py): HuggingFace에서 `kitten_tts_nano_v0_1.onnx` 모델과 `voices.npz` 파일을 로드하여 Game of Thrones 영문 텍스트를 오디오로 합성 (24000Hz 샘플레이트)
* **테스트 결과물**:
  - [`output.wav`](file:///home/toor/IsItAI/test-STTS/test-KittenTTS/output.wav): 영문으로 합성 완료된 음성 파일

---

## 2. 🐼 [test-Qwen3-TTS](file:///home/toor/IsItAI/test-STTS/test-Qwen3-TTS)
* **목적**: Qwen3-TTS 1.7B 모델 기반의 한국어 음성 합성 및 보이스 클로닝(Voice Cloning) 성능 테스트
* **개발 및 실행 환경**:
  - Python `3.11` 가상환경 (`uv venv`)
  - PyTorch 2.X (CUDA 13.0 지원 `cu130` 빌드 사용)
  - 핵심 의존성: `qwen-tts`, `soundfile`
  - RTX 5090 하드웨어 가속 최적화를 위한 `flash-attn` 설치 시도 (CUDA 13.0 호환성을 고려하여 prebuilt 또는 parallel job 제한 방식으로 설치 구성)
* **주요 스크립트**:
  - [`01-install.sh`](file:///home/toor/IsItAI/test-STTS/test-Qwen3-TTS/01-install.sh): PyTorch 2.X with CUDA 13.0 설치 및 `qwen-tts`와 `flash-attn` 빌드 스크립트
  - [`test-tts.py`](file:///home/toor/IsItAI/test-STTS/test-Qwen3-TTS/test-tts.py): `Qwen3-TTS-12Hz-1.7B-CustomVoice` 모델을 이용해 5090 GPU 가속(dtype=bfloat16)으로 기본 화자("Vivian") 기반 한국어 음성 합성
  - [`test-clone-tts.py`](file:///home/toor/IsItAI/test-STTS/test-Qwen3-TTS/test-clone-tts.py): `Qwen3-TTS-12Hz-1.7B-Base` 모델을 로드하여, 주어진 참조 오디오(`ref02.mp3`)와 참조 텍스트를 기준으로 ICL(In-Context Learning) 기법의 zero-shot 보이스 클로닝 한국어 음성 합성
* **참조 오디오**:
  - [`ref01.mp3`](file:///home/toor/IsItAI/test-STTS/test-Qwen3-TTS/ref01.mp3), [`ref02.mp3`](file:///home/toor/IsItAI/test-STTS/test-Qwen3-TTS/ref02.mp3), [`reference_0.mp3`](file:///home/toor/IsItAI/test-STTS/test-Qwen3-TTS/reference_0.mp3)
* **테스트 결과물**:
  - [`output_korean.wav`](file:///home/toor/IsItAI/test-STTS/test-Qwen3-TTS/output_korean.wav): 한국어 TTS 음성 파일 (Vivian 화자)
  - [`output_cloned_0.wav`](file:///home/toor/IsItAI/test-STTS/test-Qwen3-TTS/output_cloned_0.wav), [`output_cloned_1.wav`](file:///home/toor/IsItAI/test-STTS/test-Qwen3-TTS/output_cloned_1.wav), [`output_cloned_2.wav`](file:///home/toor/IsItAI/test-STTS/test-Qwen3-TTS/output_cloned_2.wav): 클로닝 합성 결과물

---

## 3. 💬 [test-chatterbox](file:///home/toor/IsItAI/test-STTS/test-chatterbox)
* **목적**: Resemble AI의 Chatterbox 다국어 TTS 모델 및 Docker Container 기반 Whisper STT 서비스 배포 테스트
* **개발 및 실행 환경**:
  - Python `3.11` 가상환경 및 Docker 컨테이너 환경
  - PyTorch 2.7.0 with CUDA 12.8 (`cu128`) 빌드 적용 (RTX 5090 Blackwell GPU 공식 매칭)
  - 베이스 이미지: `nvidia/cuda:12.8.0-runtime-ubuntu24.04`
  - 핵심 의존성: `chatterbox-tts==0.1.6`, `faster-whisper==1.0.3`, `fastapi`, `uvicorn`
* **주요 스크립트 & Docker 구성**:
  - [`01-venv.sh`](file:///home/toor/IsItAI/test-STTS/test-chatterbox/01-venv.sh): 로컬 venv 생성 및 PyTorch 2.7.0+cu128, `chatterbox-tts` 설치
  - [`02-docker-build.sh`](file:///home/toor/IsItAI/test-STTS/test-chatterbox/02-docker-build.sh): Dockerfile.cli를 활용하여 `chatterbox-tts` 이미지 빌드
  - [`03-run-docker.sh`](file:///home/toor/IsItAI/test-STTS/test-chatterbox/03-run-docker.sh): GPU 자원을 전체 매핑(`--gpus all`)하여 컨테이너 환경에서 초고속 한국어 음성 생성 테스트
  - [`Dockerfile.cli`](file:///home/toor/IsItAI/test-STTS/test-chatterbox/Dockerfile.cli) & [`cli_tts.py`](file:///home/toor/IsItAI/test-STTS/test-chatterbox/cli_tts.py): CLI 명령형 TTS 도구 이미지 정의. `cli_tts.py`에는 HuggingFace/Transformers 충돌(sdpa & output_attentions)을 방지하기 위한 `LlamaAttention` 강제 `eager` 모드 멍키 패치 내장.
  - [`Dockerfile.stt`](file:///home/toor/IsItAI/test-STTS/test-chatterbox/Dockerfile.stt) & [`api_stt.py`](file:///home/toor/IsItAI/test-STTS/test-chatterbox/api_stt.py): Faster-Whisper `large-v3` 모델을 로드하여 고속으로 작동하는 FastAPI STT API 서버 정의 (`/transcribe` 엔드포인트 제공)
  - [`run-tts-01.py`](file:///home/toor/IsItAI/test-STTS/test-chatterbox/run-tts-01.py): 로컬 GPU 환경에서 Chatterbox 한국어 음성 합성을 3회 반복 구동하며 소요시간을 벤치마킹
* **테스트 결과물**:
  - [`output_5090_1.wav`](file:///home/toor/IsItAI/test-STTS/test-chatterbox/output_5090_1.wav), [`output_5090_2.wav`](file:///home/toor/IsItAI/test-STTS/test-chatterbox/output_5090_2.wav), [`output_5090_3.wav`](file:///home/toor/IsItAI/test-STTS/test-chatterbox/output_5090_3.wav): RTX 5090 GPU 로컬 테스트 음성
  - [`output_docker.wav`](file:///home/toor/IsItAI/test-STTS/test-chatterbox/output_docker.wav): Docker 컨테이너 실행을 통해 합성된 결과 파일
  - **평가 노트**: 한국어 음성 합성 기능은 정상적으로 동작하나, 한영 혼용(한글과 섞인 영어) 텍스트의 경우 발음 처리가 일부 매끄럽지 않은 현상이 관찰되었습니다.

---

## 🚀 RTX 5090 GPU 구동 특이사항 및 최적화 요약

1. **CUDA 12.8 / 13.0 지원 및 5090 매핑**: RTX 5090(Blackwell 아키텍처, compute capability 12.0)의 드라이버 호환성을 고려하여 PyTorch를 최신 CUDA 12.8 (`+cu128`) 혹은 CUDA 13.0 (`+cu130`) 버전 빌드로 연동해 가속 성능을 확보했습니다.
2. **Attention 충돌 우회 (멍키 패치)**: Chatterbox 구동 과정에서 HuggingFace 트랜스포머의 `sdpa`와 `output_attentions` 인자 간 충돌이 일어나는 문제를 막기 위해, `cli_tts.py`에서 `LlamaAttention` 클래스의 초기화를 `eager` 모드로 강제 오버라이딩하는 패치를 적용했습니다.
3. **컨테이너화 및 API 서버 배포**: Whisper STT의 로드 타임을 줄이고 독립된 서비스를 구축하기 위해 FastAPI 웹서버를 Docker 이미지로 설계하여 손쉬운 GPU 서빙 체계를 검증했습니다.

---

## 🎯 AI 키오스크(Kiosk) 비즈니스 대상 기술 어필 포인트

본 테스트 프로젝트에서 수행된 작업들은 대고객 서비스의 핵심 요소인 **실시간 대화형 AI 키오스크** 구축에 있어 다음과 같이 차별화된 가치와 개발 역량을 어필할 수 있습니다.

### 1. 실시간성을 위한 초저지연(Low-Latency) 및 온디바이스/엣지 가벼운 서빙 기술 구현력
* **기술적 가치**: ONNX 포맷의 초경량 TTS 엔진(`KittenTTS Nano`) 구동 검증
* **키오스크 적용성**: 키오스크 단말기 내부(Edge)나 오프라인 매장용 소형 디바이스(NUC, 미니 PC 등) 등 네트워크 상황이 불안정하거나 제한적인 하드웨어 자원 하에서도 지연 시간(Latency) 없이 매끄러운 즉각적인 오디오 피드백 제공 가능

### 2. 최첨단 GPU 최적화 및 시스템 이슈 해결(Troubleshooting) 능력
* **기술적 가치**: 최신 **GeForce RTX 5090 (Blackwell 아키텍처)** GPU 환경 대응 및 CUDA 12.8 / 13.0, PyTorch 환경 설정 완료
* **트러블슈팅 능력**: 오픈소스 모델 구동 시 Transformers 라이브러리의 `sdpa`와 `output_attentions` 파라미터 간 충돌 문제를 해결하기 위해, `cli_tts.py`에서 `LlamaAttention` 클래스의 내부 초기화 방식을 `eager` 모드로 강제 유도하는 멍키 패치(Monkey Patch)를 직접 고안/적용하여 해결
* **키오스크 적용성**: 최신 차세대 AI 가속 하드웨어의 VRAM 및 아키텍처 특성을 정확히 분석하여 하드웨어 성능을 극한으로 끌어올리고, 라이브러리 충돌 문제를 즉각적으로 해결할 수 있는 신뢰성 높은 백엔드 운용 능력 입증

### 3. 개인화 서비스 및 브랜딩을 위한 고품질 보이스 클로닝(Voice Cloning) 기술력
* **기술적 가치**: `Qwen3-TTS-12Hz-1.7B` 모델을 활용한 고품질 한국어 TTS 및 In-Context Learning(ICL) 기법을 적용한 zero-shot 보이스 클로닝(`test-clone-tts.py`) 기술 검증
* **키오스크 적용성**: 
  - 브랜드 정체성에 특화된 전문 성우 보이스(Vivian 등)를 커스텀 탑재하여 프리미엄 키오스크 음성 인터페이스 구현
  - 점주의 목소리나 브랜드 모델의 음성을 단 수 초의 짧은 참조 샘플(`ref02.mp3`)만으로 복제하여 고객별 맞춤형 서비스 안내 및 감성적인 인터랙션 경험 제공

### 4. 마이크로서비스(MSA) 기반의 안정적이고 확장성 높은 음성 처리(STT/TTS) 아키텍처 설계
* **기술적 가치**: Docker 및 FastAPI 프레임워크 기반의 Whisper STT API 서버 구축 및 컨테이너 가속 검증
* **키오스크 적용성**:
  - 키오스크 마이크 입력(음성요청) ➡️ STT 서버(Faster-Whisper) ➡️ 자연어 처리/LLM(의도파악) ➡️ TTS 서버(Chatterbox)로 이어지는 음성 비서 파이프라인을 독립된 컨테이너 서비스로 모듈화 설계 가능
  - 프랜차이즈 매장 등 다수의 키오스크 단말 요청이 일시적으로 집중되는 환경에서도 부하 분산(Load Balancing) 및 스케일 아웃이 유연한 백엔드 아키텍처 구축 가능

