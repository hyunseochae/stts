import os
import subprocess
import platform

class AudioPlayer:
    def __init__(self):
        self.os_type = platform.system()

    def play_audio(self, file_path):
        """
        생성된 TTS 오디오 파일(MP3 / WAV)을 스피커로 재생합니다.
        """
        if not os.path.exists(file_path):
            print(f"❌ [스피커] 재생할 파일이 없습니다: {file_path}")
            return False

        print(f"🔊 [스피커] 안내 음성 재생 중...")
        try:
            if self.os_type == "Darwin":  # macOS
                subprocess.run(["afplay", file_path], check=True)
            elif self.os_type == "Linux":  # Raspberry Pi / Linux
                if file_path.endswith(".mp3"):
                    # mpg123 또는 mpv 활용
                    try:
                        subprocess.run(["mpg123", "-q", file_path], check=True)
                    except (subprocess.SubprocessError, FileNotFoundError):
                        subprocess.run(["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", file_path], check=True)
                else:
                    subprocess.run(["aplay", file_path], check=True)
            elif self.os_type == "Windows":
                os.system(f'start /min "" "{file_path}"')
            else:
                print(f"⚠️ 시스템 음성 재생 플레이어가 설치되어 있지 않습니다: {file_path}")

            print("✅ [스피커] 재생 완료")
            return True
        except Exception as e:
            print(f"❌ [스피커] 음성 재생 오류: {e}")
            return False
