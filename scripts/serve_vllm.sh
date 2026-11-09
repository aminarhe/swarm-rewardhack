#!/usr/bin/env bash
# Serve Qwen3-8B on the Vast box with tool calling ENABLED (the agents call tools).
# Run inside tmux:  tmux new -s serve ; bash scripts/serve_vllm.sh
set -euo pipefail
MODEL="${1:-Qwen/Qwen3-8B}"
pip install -q "vllm>=0.6.3"
exec vllm serve "$MODEL" \
  --enable-auto-tool-choice --tool-call-parser hermes \
  --max-model-len 16384 --gpu-memory-utilization 0.90 --port 8000
# A 24GB GPU (RTX 4090 / A5000) fits Qwen3-8B. Verify tool calling works with one
# real episode before any batch (see README "First real episode").
