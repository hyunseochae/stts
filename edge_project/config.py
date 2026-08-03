import os
from pathlib import Path

# 기본 디렉터리 경로
BASE_DIR = Path(__file__).resolve().parent
TEMP_DIR = BASE_DIR / "temp"
TEMP_DIR.mkdir(exist_ok=True)

# ----------------------------------------------------
# 1. 키오스크 메인 메뉴 목록
# ----------------------------------------------------
KIOSK_MENU = [
    "아이스 아메리카노",
    "따뜻한 아메리카노",
    "아이스 카페라떼",
    "따뜻한 카페라떼",
    "바닐라 라떼",
    "아이스티",
    "초코 라떼",
    "레몬에이드",
]

# ----------------------------------------------------
# 2. 오디오 설정 (마이크 & 스피커)
# ----------------------------------------------------
AUDIO_SAMPLE_RATE = 16000
AUDIO_CHANNELS = 1
VAD_SILENCE_DURATION = 3.0  # 음성 입력 정지 후 대기 시간 (3초로 늘려서 뜸들여도 안끊김)
VAD_THRESHOLD = 0.008       # VAD 감도 (낮을수록 작은 목소리도 인식)
RECORD_MAX_SECONDS = 15     # 최대 녹음 시간 (15초)

INPUT_AUDIO_PATH = str(TEMP_DIR / "input.wav")
OUTPUT_AUDIO_PATH = str(TEMP_DIR / "output.mp3")

# ----------------------------------------------------
# 3. STT (Speech-to-Text) 설정
# ----------------------------------------------------
# 모드: "faster-whisper" (로컬 엣지) 또는 "api" (서버 REST API)
STT_ENGINE = os.getenv("STT_ENGINE", "faster-whisper")
STT_MODEL_SIZE = os.getenv("STT_MODEL_SIZE", "base")  # tiny, base, small
STT_LANGUAGE = "ko"
STT_API_URL = os.getenv("STT_API_URL", "http://localhost:8001/api/v1/stt")

# ----------------------------------------------------
# 4. LLM (의도 분석 & 주문 파싱) 설정
# ----------------------------------------------------
# 모드: "ollama" (로컬 엣지 SLM), "openai_api", 또는 "server_api"
LLM_ENGINE = os.getenv("LLM_ENGINE", "ollama")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "qwen2.5:1.5b")
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/chat")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# ----------------------------------------------------
# 5. TTS (Text-to-Speech) 설정
# ----------------------------------------------------
# 모드: "edge-tts" (초고속 추천), "gtts", 또는 "api"
TTS_ENGINE = os.getenv("TTS_ENGINE", "edge-tts")
TTS_VOICE = os.getenv("TTS_VOICE", "ko-KR-SunHiNeural")  # ko-KR-SunHiNeural / ko-KR-InJoonNeural
TTS_API_URL = os.getenv("TTS_API_URL", "http://localhost:8003/api/v1/tts/clone")
