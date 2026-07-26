#!/usr/bin/env bash

uv venv -p 3.11
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu130

uv pip install -U qwen-tts


# for speed up 
uv pip install setuptools
# uv pip install flash-attn --no-build-isolation

# flash-attn 설치 (여러 방법 시도)
echo "Installing flash-attn... This may take a while."

# 방법 1: 사전 빌드된 wheel 사용 (가장 빠름)
echo "Trying prebuilt wheels..."
uv pip install flash-attn --no-build-isolation --find-links https://github.com/Dao-AILab/flash-attention/releases || \

# 방법 2: 병렬 작업 제한하여 빌드 (메모리 부족 방지)
(echo "Trying with limited parallel jobs..." && MAX_JOBS=4 uv pip install flash-attn --no-build-isolation) || \

# 방법 3: 건너뛰기 (선택사항)
echo "flash-attn installation failed or skipped. Qwen-TTS will work but may be slower."
