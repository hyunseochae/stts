#!/usr/bin/env bash

uv venv -p 3.11
# uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
# uv pip install --force-reinstall torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

uv pip install torch==2.7.0 torchvision==0.22.0 torchaudio==2.7.0 --index-url https://download.pytorch.org/whl/cu128

uv pip install chatterbox-tts
