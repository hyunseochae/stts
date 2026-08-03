import time
import wave
import numpy as np
import sounddevice as sd
import config

class AudioRecorder:
    def __init__(self, sample_rate=config.AUDIO_SAMPLE_RATE, channels=config.AUDIO_CHANNELS):
        self.sample_rate = sample_rate
        self.channels = channels

    def record_audio(self, output_path=config.INPUT_AUDIO_PATH, max_seconds=config.RECORD_MAX_SECONDS, silence_duration=config.VAD_SILENCE_DURATION):
        """
        마이크 입력으로 음성을 녹음하여 WAV 파일로 저장합니다.
        음성 에너지를 감지하여 사용자가 말을 마친 후 일정 시간(silence_duration)이 지나면 녹음을 종료합니다.
        """
        print("\n🎙️ [마이크] 말씀을 시작해 주세요... (주문내용 입력 중)")
        
        audio_data = []
        silence_start_time = None
        speech_detected = False
        silence_threshold = 0.015  # RMS 에너지 임계값 (배경 소음 수준에 따라 조절)

        def callback(indata, frames, time_info, status):
            nonlocal silence_start_time, speech_detected
            if status:
                print(f"[Warn] Audio input status: {status}")

            rms = np.sqrt(np.mean(indata**2))
            audio_data.append(indata.copy())

            if rms > silence_threshold:
                speech_detected = True
                silence_start_time = None
            else:
                if speech_detected and silence_start_time is None:
                    silence_start_time = time.time()

        stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype='int16',
            callback=callback
        )

        with stream:
            start_time = time.time()
            while True:
                time.sleep(0.1)
                elapsed = time.time() - start_time

                # 1. 사용자가 말을 시작한 후 silence_duration 동안 조용하면 녹음 종료
                if speech_detected and silence_start_time and (time.time() - silence_start_time >= silence_duration):
                    print("⏹️ [마이크] 음성 입력 종료 감지 (말씀 종료)")
                    break

                # 2. 최대 녹음 시간 초과 시 종료
                if elapsed >= max_seconds:
                    print("⏹️ [마이크] 최대 녹음 시간 도달")
                    break

        if not audio_data:
            print("⚠️ 녹음된 음성 데이터가 없습니다.")
            return None

        # Record된 numpy 데이터를 하나의 배열로 결합 후 WAV로 저장
        recording = np.concatenate(audio_data, axis=0)

        with wave.open(output_path, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)  # int16 = 2 bytes
            wf.setframerate(self.sample_rate)
            wf.writeframes(recording.tobytes())

        print(f"💾 [마이크] 녹음 완료: {output_path}")
        return output_path
