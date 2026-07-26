#!/usr/bin/env bash

rm -rf .venv
#uv venv -p 3.14
#uv venv -p 3.13
uv venv -p 3.12
uv pip install git+https://github.com/KittenML/KittenTTS.git

brew install espeak-ng 2>&1