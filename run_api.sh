#!/bin/bash

export PYTHONPATH="./src:$PYTHONPATH"

export API_URL="https://api.together.xyz/v1"
export API_KEY_ENV_NAME="TOGATHER_API_KEY"

python -m proverb.commands.evaluate_openai --config configs/default.yaml \
  --task_type gen_eng_literal \
  --output_dir outputs/minmax/minmax-gen-eng-literal-Somali \
  --model_name_or_path MiniMaxAI/MiniMax-M2.5 \
  --template_name=none \
  --api_delay=0.2 \
  --api_semophore=8 \
  --api_url=$API_URL \
  --api_key_env_name=$API_KEY_ENV_NAME

python -m proverb.commands.evaluate_openai --config configs/default.yaml \
  --task_type gen_eng_fig \
  --output_dir outputs/minmax/minmax-gen-eng-fig-Somali \
  --model_name_or_path MiniMaxAI/MiniMax-M2.5 \
  --template_name=none \
  --api_delay=0.2 \
  --api_semophore=8 \
  --api_url=$API_URL \
  --api_key_env_name=$API_KEY_ENV_NAME

python -m proverb.commands.evaluate_openai --config configs/default.yaml \
  --task_type gen_swa_literal \
  --output_dir outputs/minmax/minmax-gen-swa-literal-Somali \
  --model_name_or_path MiniMaxAI/MiniMax-M2.5 \
  --template_name=none \
  --api_delay=0.2 \
  --api_semophore=8 \
  --api_url=$API_URL \
  --api_key_env_name=$API_KEY_ENV_NAME

python -m proverb.commands.evaluate_openai --config configs/default.yaml \
  --task_type gen_swa_fig \
  --output_dir outputs/minmax/minmax-gen-swa-fig-Somali \
  --model_name_or_path MiniMaxAI/MiniMax-M2.5 \
  --template_name=none \
  --api_delay=0.2 \
  --api_semophore=8 \
  --api_url=$API_URL \
  --api_key_env_name=$API_KEY_ENV_NAME
