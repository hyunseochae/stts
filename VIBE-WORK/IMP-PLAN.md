# 음성 비서 백엔드 마이크로서비스(MSA) 구현 계획서 (IMP-PLAN.md)

본 문서는 키오스크 단말의 엣지 구동부를 제외하고, **Docker·FastAPI 기반 Whisper STT, LLM 의도 파악, Qwen3-TTS 보이스 클로닝 및 RTX 5090 GPU 인프라 구축**을 위한 단계별 구현 체크리스트입니다.

---

## 📌 전체 파이프라인 개요
```
[키오스크 마이크 요청] ➔ [1. Whisper STT 컨테이너] ➔ [2. LLM 의도파악] ➔ [3. Qwen3-TTS 보이스 클로닝] ➔ [음성 응답 반환]
```

---

## 🚩 Phase 1: GPU 인프라 & 베이스 환경 구축 (Infra & CUDA Setup)

- [ ] **1.1 RTX 5090 Blackwell GPU 드라이버 및 CUDA 환경 설정**
  - [ ] NVIDIA RTX 5090 GPU 인식 및 드라이버 버전 검증 (`nvidia-smi`)
  - [ ] CUDA 12.8 / 13.0 호환성 확인 및 호스트 환경 정립
- [ ] **1.2 PyTorch GPU 가속 패키지 환경 구성**
  - [ ] Python 3.11 기반 가상환경 설정 (`uv venv` 또는 `venv`)
  - [ ] RTX 5090 호환 PyTorch 휠 설치 (`--index-url https://download.pytorch.org/whl/cu130`)
  - [ ] `torch.cuda.is_available()` 및 GPU Tensor 연산 검증
- [ ] **1.3 Docker Container GPU Passthrough 환경 조성**
  - [ ] `nvidia-container-toolkit` 설치 및 설정
  - [ ] Docker 컨테이너 내부에서 `--gpus all` 접근 및 GPU 할당 테스트

---

## 🚩 Phase 2: Whisper STT 마이크로서비스 구축 (STT Service)

- [ ] **2.1 STT 엔진 모듈화 및 FastAPI REST API 개발**
  - [ ] OpenAI Whisper (`large-v3`, `turbo`) 및 `Faster-Whisper` (CTranslate2) 추론 모듈 구현
  - [ ] 음성 바이너리(WAV/MP3/PCM) 수신 엔드포인트 작성 (`POST /api/v1/stt`)
  - [ ] 한국어 인식 강제 옵션(`language='ko'`) 및 VAD (Voice Activity Detection) 필터링 적용
- [ ] **2.2 STT 출력 데이터 규격화 및 성능 측정**
  - [ ] 텍스트 결과, 인식 신뢰도, 세그먼트별 타임스탬프 JSON 응답 스키마 정의
  - [ ] 추론 시간(Inference Latency) 및 메모리 사용량 로그 모니터링 적용
- [ ] **2.3 STT 독립 컨테이너화**
  - [ ] `Dockerfile.stt` 작성 (PyTorch, ffmpeg, Faster-Whisper 패키지 포함)
  - [ ] STT 서비스 독립 실행 및 헬스체크 (`GET /health`) 구현

---

## 🚩 Phase 3: LLM 의도 파악 & 대화 제어 모듈 구축 (LLM Intent Engine)

- [ ] **3.1 STT ➔ LLM 연동 파이프라인 설계**
  - [ ] STT 변환 텍스트 수신 API 작성 (`POST /api/v1/intent`)
  - [ ] 키오스크 주문 / 메뉴 선택 / 매장 안내 의도(Intent) 파악 프로토콜 정의
- [ ] **3.2 LLM 응답 텍스트 & TTS 매핑 모듈 구현**
  - [ ] LLM 파싱 결과 기반의 최종 답변 텍스트 생성
  - [ ] TTS 모듈로 전달할 텍스트 및 음성 스타일/참조 ID 매핑 JSON 생성

---

## 🚩 Phase 4: Qwen3-TTS 보이스 클로닝 마이크로서비스 구축 (TTS Service)

- [ ] **4.1 Qwen3-TTS 모델 로딩 및 FastAPI 서버 개발**
  - [ ] `Qwen3-TTS-12Hz-1.7B` 모델 기반 서빙 엔드포인트 작성 (`POST /api/v1/tts/clone`)
  - [ ] CUDA 가속 추론 및 FP16/BF16 정밀도 설정
- [ ] **4.2 In-Context Learning (ICL) 기반 Zero-Shot 보이스 클로닝 구현**
  - [ ] 점주 및 브랜드 전속 모델의 수 초 분량 참조 음성(Reference Audio) DB 구축
  - [ ] 텍스트 합성 요청 시 참조 음성을 동적으로 주입하는 ICL 추론 파이프라인 완성
- [ ] **4.3 TTS 독립 컨테이너화**
  - [ ] `Dockerfile.tts` 작성 (Qwen3-TTS, Soundfile, CUDA 의존성 포함)
  - [ ] 독립 컨테이너 빌드 및 GPU 메모리 점유율 검증

---

## 🚩 Phase 5: 파이프라인 통합 & 백엔드 오케스트레이션 (Integration & Scale-Out)

- [ ] **5.1 API Gateway 및 End-to-End 파이프라인 연동**
  - [ ] Nginx 또는 FastAPI API Gateway 기반으로 STT ➔ LLM ➔ TTS 순차 오케스트레이션 연동
  - [ ] 키오스크 단말 ➔ 백엔드 간 통신 프로토콜 (REST API / WebSocket 스트리밍) 확정
- [ ] **5.2 부하 분산 (Load Balancing) & 스케일 아웃 설계**
  - [ ] Docker Compose 환경 구축 (`docker-compose.yml`)
  - [ ] 동시 다발적 키오스크 요청 시 STT/TTS 컨테이너 인스턴스 확장(Scale-Out) 스케줄링 검증
- [ ] **5.3 종합 트러블슈팅 및 성능 검증**
  - [ ] End-to-End 지연시간(Latency) 측정 및 병목 구간 최적화
  - [ ] RTX 5090 환경에서의 PyTorch/CUDA 파라미터 패치 및 안정성 최종 점검
