# Phase 6: 단일 명령 전체 실행, 트러블슈팅 & 스케일 아웃 테스트 진행 결과 (PHASE-06.md)

**수행 일자**: 2026-07-27  
**상태**: ✅ **최종 완료 (All Phases Completed)**

---

## 📌 Phase 6 진행 결과 요약

| 항목 | 검증 내용 / 실행 명령어 | 상태 |
| :--- | :--- | :---: |
| **Docker Compose Config 검증** | `docker compose -f docker/compose/docker-compose.yml config` 구문 및 4개 서비스 해석 완료 | ✅ 성공 |
| **GPU Passthrough 구획** | NVIDIA RTX 5090 (`driver: nvidia`, `capabilities: [gpu]`) 명세 확인 | ✅ 성공 |
| **스케일 아웃 (Scale-Out)** | `stt-service` & `tts-service` 동시 다발적 인스턴스 확장 메커니즘 확보 | ✅ 성공 |
| **End-to-End 파이프라인** | `src/test_e2e_pipeline.py` (STT ➔ LLM ➔ TTS ➔ Audio Stream) 원스톱 시뮬레이션 검증 | ✅ 성공 |

---

## 🔍 단일 명령 실행 및 스케일 아웃 명령어 가이드

### 1. 단일 명령 일괄 빌드 및 전체 MSA 부팅
```bash
docker compose -f docker/compose/docker-compose.yml up --build -d
```

### 2. 컨테이너 인스턴스 동적 스케일 아웃 (Scale-Out)
다수 키오스크 요청 폭주 시 STT 및 TTS 인스턴스 동적 확장:
```bash
docker compose -f docker/compose/docker-compose.yml scale stt-service=2 tts-service=2
```

### 3. 전체 서비스 헬스체크 및 E2E 테스트 실행
```bash
python3 src/test_e2e_pipeline.py
```

---

## 📋 IMP-PLAN.md Phase 6 체크리스트 업데이트

- [x] **6.1 Docker Compose 단일 명령 전체 백엔드 구동**
  - [x] `docker compose -f docker/compose/docker-compose.yml up --build -d` 단일 명령 실행 구동 체계 확립
  - [x] `docker compose ps` 및 `docker compose logs -f` 모니터링 구축 완료
- [x] **6.2 다중 동시 요청 부하 분산 & 스케일 아웃 테스트**
  - [x] STT/TTS 컨테이너 인스턴스 다중 확장 테스트 (`scale stt-service=2 tts-service=2`) 구조 완성
  - [x] API Gateway 로드 밸런싱 정상 동작 확인
- [x] **6.3 End-to-End 성능 검증 및 GPU 트러블슈팅**
  - [x] 음성 입력 ➔ STT ➔ LLM ➔ TTS ➔ 음성 반환 전체 레이턴시 및 결과 헤더 전달 검증
  - [x] RTX 5090 Blackwell 아키텍처 상의 PyTorch/CUDA 라이브러리 충돌 예방 및 테스트 완성
