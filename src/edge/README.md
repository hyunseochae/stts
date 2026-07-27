# Kiosk Edge Client Test Suite

키오스크 단말기(Edge Hardware) 상에서 원격 백엔드 서버(`ugai-sg.nb.is`)로 음성을 전달하고, 백엔드 마이크로서비스(STT ➔ LLM ➔ TTS) 파이프라인의 음성 합성 응답을 받아 처리하는 클라이언트 테스트 모듈입니다.

---

## 📁 파일 구조

```
src/edge/
├── kiosk_edge_client.py   # 키오스크 단말기 음성 비서 테스트 클라이언트
└── README.md              # 사용 설명서
```

---

## 🚀 사용 설명

### 1. 기본 실행 (원격 서버 `ugai-sg.nb.is` 연결)

```bash
python3 src/edge/kiosk_edge_client.py
```

### 2. 게이트웨이 주소 및 타겟 오디오 지정 실행

```bash
# 원격 서버 대상 실행
python3 src/edge/kiosk_edge_client.py --gateway http://ugai-sg.nb.is:8000 --audio /path/to/your/audio.wav

# 로컬 개발 서버 대상 실행
python3 src/edge/kiosk_edge_client.py --gateway http://localhost:8000 --audio /path/to/your/audio.wav
```

---

## 📊 주요 수신 헤더 및 출력 정보

- `X-STT-User-Text`: Whisper STT가 변환한 사용자 음성 텍스트
- `X-LLM-Intent`: LLM이 파싱한 사용자 의도 (`ORDER`, `RECOMMEND`, `INFO`)
- `X-LLM-Response-Text`: 음성으로 합성할 응답 텍스트
- `X-Pipeline-Total-Time`: 서버측 파이프라인 총 처리 소요시간 (초)
- `edge_received_voice.wav`: 수신된 Qwen3-TTS zero-shot 보이스 클로닝 합성 음성 파일
