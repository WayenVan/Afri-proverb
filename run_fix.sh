#!/bin/bash

export PYTHONPATH="./src:$PYTHONPATH"

export API_URL="https://openrouter.ai/api/v1"
export API_KEY_ENV_NAME="OPENROUTER_API_KEY"

python -m proverb.commands.evaluate_openai --config configs/default.yaml \
  --task_type gen_eng_literal \
  --output_dir outputs/gpt-5-mini/gpt-5-mini-gen-eng-literal-Somali \
  --model_name_or_path openai/gpt-5-chat \
  --template_name=none \
  --location=Somali \
  --language=somali \
  --api_delay=1.0 \
  --api_semophore=8 \
  --api_url=$API_URL \
  --api_key_env_name=$API_KEY_ENV_NAME

python -m proverb.commands.evaluate_openai --config configs/default.yaml \
  --task_type gen_eng_fig \
  --output_dir outputs/gpt-5-mini/gpt-5-mini-gen-eng-fig-Somali \
  --model_name_or_path openai/gpt-5-chat \
  --template_name=none \
  --location=Somali \
  --language=somali \
  --api_delay=1.0 \
  --api_semophore=8 \
  --api_url=$API_URL \
  --api_key_env_name=$API_KEY_ENV_NAME

python -m proverb.commands.evaluate_openai --config configs/default.yaml \
  --task_type gen_swa_literal \
  --output_dir outputs/gpt-5-mini/gpt-5-mini-gen-swa-literal-Somali \
  --model_name_or_path openai/gpt-5-chat \
  --location=Somali \
  --language=somali \
  --template_name=none \
  --api_delay=1.0 \
  --api_semophore=8 \
  --api_url=$API_URL \
  --api_key_env_name=$API_KEY_ENV_NAME

python -m proverb.commands.evaluate_openai --config configs/default.yaml \
  --task_type gen_swa_fig \
  --output_dir outputs/gpt-5-mini/gpt-5-mini-gen-swa-fig-Somali \
  --model_name_or_path openai/gpt-5-chat \
  --location=Somali \
  --language=somali \
  --template_name=none \
  --api_delay=1.0 \
  --api_semophore=8 \
  --api_url=$API_URL \
  --api_key_env_name=$API_KEY_ENV_NAME
