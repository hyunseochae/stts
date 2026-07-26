#!/usr/bin/env bash

docker run --rm --gpus all \
  -v $(pwd):/app/out \
  chatterbox-tts "안녕하세요. 도커 이미지로 고속 음성 합성을 시작합니다." \
  --output /app/out/output_docker.wav