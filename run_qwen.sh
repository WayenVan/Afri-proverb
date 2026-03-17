export PYTHONPATH="./src:$PYTHONPATH"
export CUDA_LAUNCH_BLOCKING=1

accelerate launch --num_processes=2 --mixed_precision=bf16 \
  -m proverb.commands.evaluate --config configs/default.yaml \
  --task_type gen_eng_literal \
  --output_dir outputs/qwen3-4b-few-shots/qwen3-4b-few-shots-gen-eng-literal-Tanzania \
  --template_name qwen3 \
  --model_name_or_path Qwen/Qwen3-4B \
  --few_shot_num 1

accelerate launch --num_processes=2 --mixed_precision=bf16 \
  -m proverb.commands.evaluate --config configs/default.yaml \
  --task_type gen_eng_fig \
  --output_dir outputs/qwen3-4b-few-shots/qwen3-4b-few-shots-gen-eng-fig-Tanzania \
  --template_name qwen3 \
  --model_name_or_path Qwen/Qwen3-4B \
  --few_shot_num 1

accelerate launch --num_processes=2 --mixed_precision=bf16 \
  -m proverb.commands.evaluate --config configs/default.yaml \
  --task_type gen_swa_literal \
  --output_dir outputs/qwen3-4b-few-shots/qwen3-4b-few-shots-gen-swa-literal-Tanzania \
  --template_name qwen3 \
  --model_name_or_path Qwen/Qwen3-4B \
  --few_shot_num 1

accelerate launch --num_processes=2 --mixed_precision=bf16 \
  -m proverb.commands.evaluate --config configs/default.yaml \
  --task_type gen_swa_fig \
  --output_dir outputs/qwen3-4b-few-shots/qwen3-4b-few-shots-gen-swa-fig-Tanzania \
  --template_name qwen3 \
  --model_name_or_path Qwen/Qwen3-4B \
  --few_shot_num 1

# --------------------------------------------
