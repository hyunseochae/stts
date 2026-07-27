# Kiosk Edge Client Test Suite

키오스크 단말기(Edge Hardware 및 Mac 환경) 상에서 원격 백엔드 서버(`ugai-sg.nb.is`)로 음성을 전달하고, 백엔드 마이크로서비스(STT ➔ LLM ➔ TTS) 파이프라인의 음성 합성 응답을 받아 스피커로 출력하는 클라이언트 테스트 모듈입니다.

---

## 📁 파일 구조

```
src/edge/
├── mac-test.py            # Mac 마이크 실시간 녹음 & 스피커 응답 재생 대화형 클라이언트
├── kiosk_edge_client.py   # 기존 오디오 파일 기반 키오스크 단말기 시뮬레이션 클라이언트
├── requirements.txt       # 엣지 단말용 필요 패키지 명세
└── README.md              # 사용 설명서
```

---

## 🚀 사용 설명

### 1. Mac 실시간 마이크 대화형 테스트 (`mac-test.py`)
Mac 마이크로 4초간 음성을 녹음하여 원격 게이트웨이(`ugai-sg.nb.is`)로 전송한 뒤, AI 키오스크 답변 음성을 Mac 스피커(`afplay`)로 즉시 재생합니다.

```bash
# 기본 실행 (Enter 키 입력 후 녹음 시작)
python3 src/edge/mac-test.py

# 녹음 시간(예: 6초) 지정 실행
python3 src/edge/mac-test.py --duration 6 --gateway http://ugai-sg.nb.is:8000
```

### 2. 파일 기반 엣지 단말기 테스트 (`kiosk_edge_client.py`)

```bash
# 원격 서버 대상 실행
python3 src/edge/kiosk_edge_client.py --gateway http://ugai-sg.nb.is:8000 --audio /path/to/your/audio.wav
```

---

## ⚙️ 필요 의존성 설치
```bash
pip install -r src/edge/requirements.txt
```
