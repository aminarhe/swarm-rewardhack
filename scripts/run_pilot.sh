#!/usr/bin/env bash
# Connect Inspect to the served vLLM and run both conditions. Run in a second tmux
# pane while serve_vllm.sh holds the first.
#   tmux new -s run ; bash scripts/run_pilot.sh Qwen/Qwen3-8B 10
set -euo pipefail
MODEL_NAME="${1:-Qwen/Qwen3-8B}"
EPOCHS="${2:-10}"
export OPENAI_BASE_URL="${OPENAI_BASE_URL:-http://localhost:8000/v1}"
export OPENAI_API_KEY="${OPENAI_API_KEY:-EMPTY}"
MODEL="openai/$MODEL_NAME"

for OBS in true false; do
  echo ">>> condition observed=$OBS"
  inspect eval swarm_env/task.py@swarm_task -T observed=$OBS \
    --model "$MODEL" --epochs "$EPOCHS" --max-connections 8 \
    --temperature 0.7 --log-dir "logs/pilot_obs_$OBS"
  # Qwen3 thinking is a CONDITION (CLAUDE.md rule 10). This serves with thinking on
  # by default; to turn it off add: -M extra_body='{"chat_template_kwargs":{"enable_thinking":false}}'
  # Confirm which you ran by opening the transcript in `inspect view`.
done
python -m swarm_env.analyze logs/pilot_obs_true logs/pilot_obs_false
