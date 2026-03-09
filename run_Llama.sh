export CUDA_VISIBLE_DEVICES=0
export PYTHONPATH="./src:$PYTHONPATH"
export CUDA_LAUNCH_BLOCKING=1
# -------------------------GEMMA 4B-----------------------------------

accelerate launch --num_processes=1 --mixed_precision=bf16 \
  -m proverb.commands.evaluate --config configs/default.yaml \
  --task_type gen_eng_literal \
  --output_dir outputs/llama-3.2-3b/llama3.2-3b-it-gen-eng-literal-Kenya \
  --model_name_or_path meta-llama/Llama-3.2-3B-Instruct \
  --few_shot_num 1

accelerate launch --num_processes=1 --mixed_precision=bf16 \
  -m proverb.commands.evaluate --config configs/default.yaml \
  --task_type gen_eng_fig \
  --output_dir outputs/llama-3.2-3b/llama3.2-3b-it-gen-eng-fig-Kenya \
  --model_name_or_path meta-llama/Llama-3.2-3B-Instruct
#
accelerate launch --num_processes=1 --mixed_precision=bf16 \
  -m proverb.commands.evaluate --config configs/default.yaml \
  --task_type gen_swa_literal \
  --output_dir outputs/llama-3.2-3b/llama3.2-3b-it-gen-swa-literal-Kenya \
  --model_name_or_path meta-llama/Llama-3.2-3B-Instruct

accelerate launch --num_processes=1 --mixed_precision=bf16 \
  -m proverb.commands.evaluate --config configs/default.yaml \
  --task_type gen_swa_fig \
  --output_dir outputs/llama-3.2-3b/llama3.2-3b-it-gen-swa-fig-Kenya \
  --model_name_or_path meta-llama/Llama-3.2-3B-Instruct

# accelerate launch --num_processes=1 --mixed_precision=bf16 \
#   -m proverb.commands.evaluate --config configs/default.yaml \
#   --task_type gen_eng_literal \
#   --output_dir outputs/llama3.2-3b-it-gen-eng-literal-Kenya \
#   --model_name_or_path meta-llama/Llama-3.2-3B-Instruct \
#   --location Somali \
#   --language somali
#
# accelerate launch --num_processes=2 --mixed_precision=bf16 \
#   -m proverb.commands.evaluate --config configs/default.yaml \
#   --task_type gen_eng_fig \
#   --output_dir outputs/llama3.2-3b-it-gen-eng-fig-Kenya \
#   --model_name_or_path meta-llama/Llama-3.2-3B-Instruct \
#   --location Somali \
#   --language somali
#
# accelerate launch --num_processes=2 --mixed_precision=bf16 \
#   -m proverb.commands.evaluate --config configs/default.yaml \
#   --task_type gen_swa_literal \
#   --output_dir outputs/llama3.2-3b-it-gen-swa-literal-Kenya \
#   --model_name_or_path meta-llama/Llama-3.2-3B-Instruct \
#   --location Somali \
#   --language somali
#
# accelerate launch --num_processes=2 --mixed_precision=bf16 \
#   -m proverb.commands.evaluate --config configs/default.yaml \
#   --task_type gen_swa_fig \
#   --output_dir outputs/llama3.2-3b-it-gen-swa-fig-Kenya \
#   --model_name_or_path meta-llama/Llama-3.2-3B-Instruct \
#   --location Somali \
#   --language somali
#
# accelerate launch --num_processes=2 --mixed_precision=bf16 \
#   -m proverb.commands.evaluate --config configs/default.yaml \
#   --task_type gen_eng_literal \
#   --output_dir outputs/llama3.2-3b-it-gen-eng-literal-Kenya \
#   --model_name_or_path meta-llama/Llama-3.2-3B-Instruct \
#   --location Ethiopia \
#   --language borana,burji
#
# accelerate launch --num_processes=2 --mixed_precision=bf16 \
#   -m proverb.commands.evaluate --config configs/default.yaml \
#   --task_type gen_eng_fig \
#   --output_dir outputs/llama3.2-3b-it-gen-eng-fig-Kenya \
#   --model_name_or_path meta-llama/Llama-3.2-3B-Instruct \
#   --location Ethiopia \
#   --language borana,burji
#
# accelerate launch --num_processes=2 --mixed_precision=bf16 \
#   -m proverb.commands.evaluate --config configs/default.yaml \
#   --task_type gen_swa_literal \
#   --output_dir outputs/llama3.2-3b-it-gen-swa-literal-Kenya \
#   --model_name_or_path meta-llama/Llama-3.2-3B-Instruct \
#   --location Ethiopia \
#   --language borana,burji
#
# accelerate launch --num_processes=2 --mixed_precision=bf16 \
#   -m proverb.commands.evaluate --config configs/default.yaml \
#   --task_type gen_swa_fig \
#   --output_dir outputs/llama3.2-3b-it-gen-swa-fig-Kenya \
#   --model_name_or_path meta-llama/Llama-3.2-3B-Instruct \
#   --location Ethiopia \
#   --language borana,burji
