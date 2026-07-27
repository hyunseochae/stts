#!/usr/bin/env bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "  Setting up Whisper Test Environment    "
echo "=========================================="

# 1. Create Virtual Environment using uv
echo "[1/3] Creating virtual environment (.venv)..."
uv venv -p 3.11 .venv

# 2. Install PyTorch with CUDA 13.0 support (for RTX 5090 Blackwell GPU)
echo "[2/3] Installing PyTorch with CUDA 13.0 support..."
uv pip install torch torchaudio torchvision --index-url https://download.pytorch.org/whl/cu130 || uv pip install torch torchaudio torchvision

# 3. Install Whisper dependencies
echo "[3/3] Installing Whisper packages..."
uv pip install -r requirements.txt

echo "=========================================="
echo "  Installation Complete!                "
echo "  Activate with: source .venv/bin/activate"
echo "=========================================="
