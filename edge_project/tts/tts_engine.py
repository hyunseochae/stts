import asyncio
import os
import requests
import config

class TTSEngine:
    def __init__(self, engine_type=config.TTS_ENGINE, voice=config.TTS_VOICE):
        self.engine_type = engine_type
        self.voice = voice

    def generate_speech(self, text, output_path=config.OUTPUT_AUDIO_PATH):
        """
        안내문 텍스트를 음성 오디오 파일(MP3)로 합성하여 저장합니다.
        """
        if not text.strip():
            return False

        print(f"🗣️ [TTS] 안내 음성 합성 시작... (엔진: {self.engine_type})")

        if self.engine_type == "edge-tts":
            return asyncio.run(self._generate_edge_tts(text, output_path))
        elif self.engine_type == "gtts":
            return self._generate_gtts(text, output_path)
        elif self.engine_type == "api":
            return self._generate_api_tts(text, output_path)
        else:
            print(f"⚠️ 알 수 없는 TTS 엔진 {self.engine_type}. gTTS로 대체합니다.")
            return self._generate_gtts(text, output_path)

    async def _generate_edge_tts(self, text, output_path):
        try:
            import edge_tts
            communicate = edge_tts.Communicate(text, self.voice)
            await communicate.save(output_path)
            print(f"💾 [TTS] 음성 합성 파일 저장 완료: {output_path}")
            return output_path
        except Exception as e:
            print(f"❌ [Edge-TTS Error] {e}. gTTS 폴백 실행...")
            return self._generate_gtts(text, output_path)

    def _generate_gtts(self, text, output_path):
        try:
            from gtts import gTTS
            tts = gTTS(text=text, lang='ko')
            tts.save(output_path)
            print(f"💾 [TTS] gTTS 음성 합성 파일 저장 완료: {output_path}")
            return output_path
        except Exception as e:
            print(f"❌ [gTTS Error] 음성 합성 실패: {e}")
            return False

    def _generate_api_tts(self, text, output_path):
        try:
            payload = {"text": text}
            res = requests.post(config.TTS_API_URL, json=payload, timeout=10)
            if res.status_code == 200:
                with open(output_path, "wb") as f:
                    f.write(res.content)
                print(f"💾 [TTS API] 음성 합성 파일 수신 완료: {output_path}")
                return output_path
            else:
                print(f"❌ [TTS API Error] HTTP {res.status_code}. gTTS 폴백 실행")
                return self._generate_gtts(text, output_path)
        except Exception as e:
            print(f"❌ [TTS API Error] {e}")
            return self._generate_gtts(text, output_path)
