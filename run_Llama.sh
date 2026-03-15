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
MODEL_NAME="meta-llama/Llama-3.2-3B-Instruct"
MODEL_SHORT="llama3.2-3b"
TEMPLATE="llama3"

# Loop through all locations
for location in "${!LOCATIONS[@]}"; do
  language="${LOCATIONS[$location]}"
  
  # Loop through all task types
  for task_type in "${TASK_TYPES[@]}"; do
    output_dir="outputs/${MODEL_SHORT}/${MODEL_SHORT}-${task_type}-${location}"
    
    # Create output directory if it doesn't exist
    mkdir -p "$output_dir"
    
    echo "Running: Location=$location, Task=$task_type"
    
    accelerate launch --num_processes=2 --mixed_precision=bf16 \
      -m proverb.commands.evaluate --config configs/default.yaml \
      --task_type "$task_type" \
      --output_dir "$output_dir" \
      --template_name "$TEMPLATE" \
      --model_name_or_path "$MODEL_NAME" \
      --location "$location" \
      --language "$language"
  done
done

echo "All evaluations completed!"
