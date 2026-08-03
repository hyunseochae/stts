import os
import requests
import config

class STTEngine:
    def __init__(self, engine_type=config.STT_ENGINE, model_size=config.STT_MODEL_SIZE):
        self.engine_type = engine_type
        self.model_size = model_size
        self.whisper_model = None

        if self.engine_type == "faster-whisper":
            try:
                from faster_whisper import WhisperModel
                print(f"⚙️ [STT] 로컬 faster-whisper ('{self.model_size}') 모델 로딩 중...")
                # 라즈베리파이 CPU 모드 설정 (device="cpu", compute_type="int8")
                self.whisper_model = WhisperModel(
                    self.model_size,
                    device="cpu",
                    compute_type="int8"
                )
                print("✅ [STT] faster-whisper 모델 초기화 완료")
            except ImportError:
                print("⚠️ [STT] faster-whisper 패키지가 설치되어 있지 않습니다. API 모드로 대체 준비합니다.")
                self.engine_type = "api"

    def transcribe(self, audio_file_path):
        """
        녹음된 오디오 파일을 텍스트로 변환합니다.
        """
        if not os.path.exists(audio_file_path):
            print(f"❌ [STT] 오디오 파일이 존재하지 않습니다: {audio_file_path}")
            return ""

        print(f"📝 [STT] 음성 인식(STT) 변환 시작...")

        if self.engine_type == "faster-whisper" and self.whisper_model:
            try:
                segments, info = self.whisper_model.transcribe(
                    audio_file_path,
                    language=config.STT_LANGUAGE,
                    beam_size=1
                )
                text = "".join([segment.text for segment in segments]).strip()
                print(f"🎯 [STT 결과]: \"{text}\"")
                return text
            except Exception as e:
                print(f"❌ [STT Error] faster-whisper 처리 중 오류: {e}")
                return ""

        elif self.engine_type == "api":
            try:
                with open(audio_file_path, "rb") as f:
                    files = {"file": f}
                    response = requests.post(config.STT_API_URL, files=files, timeout=10)
                    
                if response.status_code == 200:
                    result = response.json()
                    text = result.get("text", result.get("transcript", "")).strip()
                    print(f"🎯 [STT API 결과]: \"{text}\"")
                    return text
                else:
                    print(f"❌ [STT API Error] HTTP {response.status_code}: {response.text}")
                    return ""
            except Exception as e:
                print(f"❌ [STT API Error] 서버 요청 실패: {e}")
                return ""
        else:
            print(f"❌ [STT Error] 알 수 없는 STT 엔진: {self.engine_type}")
            return ""
