# 음성 비서 백엔드 마이크로서비스(MSA) 구현 계획서 (IMP-PLAN.md)

본 문서는 키오스크 단말의 엣지 구동부를 제외하고, **Docker · Docker Compose 기반의 Whisper STT, LLM 의도 파악, Qwen3-TTS 보이스 클로닝 마이크로서비스 및 RTX 5090 GPU 인프라 구축**을 위한 단계별 실행 계획 체크리스트입니다.

---

## 📌 전체 파이프라인 개요
```
[키오스크 요청] ➔ [API Gateway] ➔ [1. STT Container] ➔ [2. LLM Container] ➔ [3. TTS Container] ➔ [음성 반환]
                                   └─────── Docker Compose (MSA Orchestration) ───────┘
```

---

## 🚩 Phase 1: GPU 인프라 & 베이스 환경 구축 (Infra & CUDA Setup) - ✅ 완료

- [x] **1.1 RTX 5090 Blackwell GPU 드라이버 및 CUDA 환경 설정**
  - [x] NVIDIA RTX 5090 GPU 인식 및 드라이버 버전 검증 (`nvidia-smi`)
  - [x] CUDA 12.8 / 13.0 호환성 확인 및 호스트 환경 정립
- [x] **1.2 PyTorch GPU 가속 패키지 환경 구성**
  - [x] Python 3.11 기반 가상환경 설정 (`uv venv` 또는 `venv`)
  - [x] RTX 5090 호환 PyTorch 휠 설치 (`--index-url https://download.pytorch.org/whl/cu130`)
  - [x] `torch.cuda.is_available()` 및 GPU Tensor 연산 검증
- [x] **1.3 Docker Container GPU Passthrough 환경 조성**
  - [x] `nvidia-container-toolkit` 설치 및 Docker 커스텀 런타임 설정
  - [x] Docker 컨테이너 내부에서 GPU 접근 (`--gpus all`) 테스트

---

## 🚩 Phase 2: Whisper STT 마이크로서비스 컨테이너 개발 (STT Service) - ✅ 완료

- [x] **2.1 STT 엔진 모듈화 및 FastAPI REST API 개발**
  - [x] OpenAI Whisper (`large-v3`, `turbo`) 및 `Faster-Whisper` (CTranslate2) 추론 모듈 구현
  - [x] 음성 바이너리(WAV/MP3/PCM) 수신 엔드포인트 작성 (`POST /api/v1/stt`)
  - [x] 한국어 인식 강제 옵션(`language='ko'`) 및 VAD (Voice Activity Detection) 필터링 적용
- [x] **2.2 STT 출력 데이터 규격화 및 성능 측정**
  - [x] 텍스트 결과, 인식 신뢰도, 세그먼트별 타임스탬프 JSON 응답 스키마 정의
  - [x] 추론 시간(Inference Latency) 및 메모리 사용량 로그 모니터링 적용
- [x] **2.3 STT 전용 Dockerfile 작성 (`docker/image/stt-service/Dockerfile`)**
  - [x] `docker/image/stt-service/Dockerfile` 작성 (PyTorch, ffmpeg, Faster-Whisper 포함)
  - [x] `src/stt-service/` 디렉토리에 백엔드 소스코드 전용 구축 완료

---

## 🚩 Phase 3: LLM 의도 파악 & 대화 제어 모듈 개발 (LLM Intent Engine) - ✅ 완료

- [x] **3.1 STT ➔ LLM 연동 파이프라인 설계**
  - [x] STT 변환 텍스트 수신 API 작성 (`POST /api/v1/intent`)
  - [x] 키오스크 주문 / 메뉴 선택 / 매장 안내 의도(Intent) 파악 프로토콜 정의
- [x] **3.2 LLM 응답 텍스트 & TTS 매핑 모듈 구현**
  - [x] LLM 파싱 결과 기반의 최종 답변 텍스트 생성
  - [x] TTS 모듈로 전달할 텍스트 및 음성 스타일/참조 ID 매핑 JSON 생성
- [x] **3.3 LLM 전용 Dockerfile 작성 (`docker/image/llm-service/Dockerfile`)**
  - [x] `docker/image/llm-service/Dockerfile` 작성 및 컨테이너 독립화
  - [x] `src/llm-service/` 디렉토리에 소스코드 전용 구축 완료

---

## 🚩 Phase 4: Qwen3-TTS 보이스 클로닝 컨테이너 개발 (TTS Service)

- [ ] **4.1 Qwen3-TTS 모델 로딩 및 FastAPI 서버 개발**
  - [ ] `Qwen3-TTS-12Hz-1.7B` 모델 기반 서빙 엔드포인트 작성 (`POST /api/v1/tts/clone`)
  - [ ] CUDA 가속 추론 및 FP16/BF16 정밀도 설정
- [ ] **4.2 In-Context Learning (ICL) 기반 Zero-Shot 보이스 클로닝 구현**
  - [ ] 점주 및 브랜드 전속 모델의 수 초 분량 참조 음성(Reference Audio) DB 구축
  - [ ] 텍스트 합성 요청 시 참조 음성을 동적으로 주입하는 ICL 추론 파이프라인 완성
- [ ] **4.3 TTS 전용 Dockerfile 작성 (`Dockerfile.tts`)**
  - [ ] Qwen3-TTS, Soundfile, CUDA 의존성 포함 `Dockerfile.tts` 작성
  - [ ] 독립 컨테이너 빌드 및 GPU 메모리 점유율 검증

---

## 🚩 Phase 5: Docker Compose 오케스트레이션 구동 환경 구성 (Docker Compose Setup)

- [ ] **5.1 Docker Compose 설정 파일 작성 (`docker-compose.yml`)**
  - [ ] `stt-service`, `llm-service`, `tts-service`, `api-gateway` 4개 서비스 정의
  - [ ] GPU 리소스 할당 구획 명시 (`deploy.resources.reservations.devices` nvidia GPU 설정)
  - [ ] 컨테이너 간 분리된 내부 프라이빗 브릿지 네트워크 (`voice-assistant-net`) 구축
  - [ ] 모델 및 참조 음성 데이터 persistence 볼륨 바인딩 (`./models`, `./ref_voices`)
- [ ] **5.2 환경 변수 및 의존성 헬스체크 설정**
  - [ ] 서비스 공통 환경 변수 파일 (`.env`) 작성
  - [ ] 컨테이너 시퀀스 부팅을 위한 `healthcheck` 및 `depends_on: condition: service_healthy` 지정
- [ ] **5.3 API Gateway (Nginx / FastAPI Router) 오케스트레이션 연동**
  - [ ] 외부 키오스크 단말 요청 수신 API Gateway 라우팅 설정
  - [ ] Gateway ➔ STT ➔ LLM ➔ TTS 모듈 간 내부 네트워크 호스트명 통신 라우팅

---

## 🚩 Phase 6: 단일 명령 전체 실행, 트러블슈팅 & 스케일 아웃 테스트 (Execution & Scaling)

- [ ] **6.1 Docker Compose 단일 명령 전체 백엔드 구동**
  - [ ] `docker compose up --build -d` 단일 명령 실행으로 전체 MSA 수월한 부팅 확인
  - [ ] `docker compose ps` 및 `docker compose logs -f` 모니터링 체계 점검
- [ ] **6.2 다중 동시 요청 부하 분산 & 스케일 아웃 테스트**
  - [ ] STT/TTS 컨테이너 인스턴스 다중 확장 테스트 (`docker compose scale stt-service=2 tts-service=2`)
  - [ ] API Gateway 로드 밸런싱 정상 동작 검증
- [ ] **6.3 End-to-End 성능 검증 및 GPU 트러블슈팅**
  - [ ] 음성 입력 ➔ STT ➔ LLM ➔ TTS ➔ 음성 반환 전체 레이턴시 측정 및 최적화
  - [ ] RTX 5090 Blackwell 아키텍처 상의 PyTorch/CUDA 라이브러리 충돌 패치 검증
