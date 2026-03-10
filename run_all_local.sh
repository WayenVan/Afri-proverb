#!/bin/bash

export PYTHONPATH="./src:$PYTHONPATH"
export CUDA_LAUNCH_BLOCKING=1

# Define locations and their languages
declare -A LOCATIONS
LOCATIONS["Kenya"]="digo, ekegusii, gikuyu, kamba, luo, maasai, meru, nandi, nubian_2, nubian, nyala, olusamia, orma, rendille, samburu, teso, tugen, turkana"
LOCATIONS["Tanzania"]="gweno, kihangaza, kihara, makonde, nyaturu, pare, sukuma, zigula"
LOCATIONS["DRC"]="kwele, tetela, bangubangu, hema, hemba, holoholo, nande, taabwa, tshiluba"
LOCATIONS["Uganda"]="alur, chiga, ganda, rufumbira, runyoro, soga, tooro"
LOCATIONS["Somali"]="somali"
LOCATIONS["Ethiopia"]="borana, burji"

# Define task types
TASK_TYPES=("gen_eng_literal" "gen_eng_fig" "gen_swa_literal" "gen_swa_fig")

# Model configuration
MODEL_NAME="Qwen/Qwen3-4B"
MODEL_SHORT="qwen3-4b"
TEMPLATE="qwen3"

# Log file
LOG_FILE="run_$(date +%Y%m%d_%H%M%S).log"

echo "Starting evaluations at $(date)" | tee -a "$LOG_FILE"
echo "Log file: $LOG_FILE" | tee -a "$LOG_FILE"

# Loop through all locations
for location in "${!LOCATIONS[@]}"; do
  language="${LOCATIONS[$location]}"
  
  # Loop through all task types
  for task_type in "${TASK_TYPES[@]}"; do
    output_dir="outputs/${MODEL_SHORT}/${MODEL_SHORT}-${task_type}-${location}"
    
    # Create output directory if it doesn't exist
    mkdir -p "$output_dir"
    
    echo "" | tee -a "$LOG_FILE"
    echo "========================================" | tee -a "$LOG_FILE"
    echo "Running: Location=$location, Task=$task_type" | tee -a "$LOG_FILE"
    echo "Started at: $(date)" | tee -a "$LOG_FILE"
    echo "========================================" | tee -a "$LOG_FILE"
    
    accelerate launch --num_processes=2 --mixed_precision=bf16 \
      -m proverb.commands.evaluate --config configs/default.yaml \
      --task_type "$task_type" \
      --output_dir "$output_dir" \
      --template_name "$TEMPLATE" \
      --model_name_or_path "$MODEL_NAME" \
      --location "$location" \
      --language "$language" 2>&1 | tee -a "$LOG_FILE"
    
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
      echo "✓ Completed: $location - $task_type at $(date)" | tee -a "$LOG_FILE"
    else
      echo "✗ Failed: $location - $task_type at $(date)" | tee -a "$LOG_FILE"
    fi
  done
done

echo "" | tee -a "$LOG_FILE"
echo "All evaluations completed at $(date)" | tee -a "$LOG_FILE"
