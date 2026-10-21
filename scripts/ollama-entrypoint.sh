#!/usr/bin/env bash
set -euo pipefail
# Import the lab model once; inference then reads Linux-native storage.
python /usr/local/bin/import-model-cache.py
exec /bin/ollama serve
