import os
import torch
import torchaudio
import argparse
import sys
from pathlib import Path

# Transformers의 sdpa와 output_attentions 충돌 방지를 위한 유연한 멍키 패치
import transformers
from transformers.models.llama.modeling_llama import LlamaAttention

# LlamaAttention이 sdpa 대신 항상 eager를 사용하도록 유도
def patched_init(self, config, *args, **kwargs):
    # 모델 빌드 시 sdpa 사용을 강제로 차단
    config._attn_implementation = "eager"
    return self.__original_init__(config, *args, **kwargs)

# 패치 적용
if not hasattr(LlamaAttention, "__original_init__"):
    LlamaAttention.__original_init__ = LlamaAttention.__init__
    LlamaAttention.__init__ = patched_init

from chatterbox import ChatterboxMultilingualTTS

def main():
    parser = argparse.ArgumentParser(description="Chatterbox TTS CLI")
    parser.add_argument("text", type=str, help="Text to synthesize")
    parser.add_argument("--output", type=str, default="output.wav", help="Output wav file path")
    parser.add_argument("--lang", type=str, default="ko", help="Language ID (default: ko)")
    
    args = parser.parse_args()

    # RTX 5090 (sm_120) 지원을 위해 PyTorch 2.7.0+cu128 환경에서 실행 권장
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    try:
        print("Loading model...")
        # Transformers의 sdpa와 output_attentions 충돌 방지를 위한 환경 변수 설정
        os.environ["ACCELERATE_USE_FSDP"] = "false"
        
        # Chatterbox 내부에서 transformers를 로드할 때 sdpa를 사용하지 않도록 
        # 환경 변수 또는 패치를 시도합니다.
        # 실행 시점에 경고를 무시하거나 설정을 강제함.
        model = ChatterboxMultilingualTTS.from_pretrained(device=device)
        
        print(f"Synthesizing: {args.text}")
        audio = model.generate(
            text=args.text,
            language_id=args.lang
        )
        
        output_path = Path(args.output)
        torchaudio.save(str(output_path), audio.cpu(), sample_rate=model.sr)
        print(f"Saved to {output_path}")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
