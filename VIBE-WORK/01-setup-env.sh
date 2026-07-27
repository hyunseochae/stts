#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=================================================="
echo " [Phase 1] Setting up GPU & PyTorch Base Environment"
echo "=================================================="

# 1. Create Virtual Environment using uv
echo "[1/3] Creating virtual environment (.venv)..."
uv venv -p 3.11 .venv

# 2. Install PyTorch with CUDA 13.0 support for RTX 5090
echo "[2/3] Installing PyTorch with CUDA 13.0 (cu130)..."
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu130 || uv pip install torch torchvision torchaudio

# 3. Verify PyTorch CUDA & GPU Environment
echo "[3/3] Verifying PyTorch CUDA support..."
./.venv/bin/python -c "
import torch
print('PyTorch Version:', torch.__version__)
print('CUDA Available :', torch.cuda.is_available())
if torch.cuda.is_available():
    print('Device Name     :', torch.cuda.get_device_name(0))
    print('Device Count    :', torch.cuda.device_count())
    x = torch.randn(1000, 1000, device='cuda')
    y = torch.matmul(x, x)
    print('GPU Tensor Matmul Test Success! Shape:', y.shape)
else:
    print('CUDA is not directly active in this PyTorch build.')
"

echo "=================================================="
echo " Phase 1 Base Environment Setup Complete!"
echo "=================================================="
