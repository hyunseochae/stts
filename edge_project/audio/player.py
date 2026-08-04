import os
import subprocess
import platform

class AudioPlayer:
    def __init__(self):
        self.os_type = platform.system()

    def play_audio(self, file_path):
        """
        생성된 TTS 오디오 파일(MP3 / WAV)을 스피커로 재생합니다.
        스피커가 없는 환경(라즈베리파이 헤드리스 등)에서는 예외를 차단하고 저장 위치를 안내합니다.
        """
        if not file_path or not os.path.exists(file_path):
            print(f"❌ [스피커] 재생할 파일이 없습니다: {file_path}")
            return False

        print(f"🔊 [스피커] 안내 음성 재생 시도 중... ({file_path})")
        try:
            if self.os_type == "Darwin":  # macOS
                subprocess.run(["afplay", file_path], check=True)
            elif self.os_type == "Linux":  # Raspberry Pi / Linux
                played = False
                if file_path.endswith(".mp3"):
                    for cmd in [["mpg123", "-q", file_path], ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", file_path], ["cvlc", "--play-and-exit", file_path]]:
                        try:
                            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            played = True
                            break
                        except (subprocess.SubprocessError, FileNotFoundError):
                            continue
                else:
                    try:
                        subprocess.run(["aplay", file_path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        played = True
                    except (subprocess.SubprocessError, FileNotFoundError):
                        pass

                if not played:
                    print(f"⚠️ [스피커 알림] 물리 스피커 장치가 없거나 오디오 재생 도구가 없습니다.")
                    print(f"   ➔ 생성된 TTS 음성 파일: '{file_path}'")
                    return True
            elif self.os_type == "Windows":
                os.system(f'start /min "" "{file_path}"')
            else:
                print(f"⚠️ 시스템 음성 재생 플레이어가 설치되어 있지 않습니다: {file_path}")

            print("✅ [스피커] 재생 완료")
            return True
        except Exception as e:
            print(f"⚠️ [스피커 알림] 재생 실패 (스피커 연결 없음): {e}")
            print(f"   ➔ 생성된 TTS 음성 파일: '{file_path}'")
            return True
