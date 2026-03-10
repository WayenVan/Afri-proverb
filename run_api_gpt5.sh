#!/bin/bash

export PYTHONPATH="./src:$PYTHONPATH"

export API_URL="https://openrouter.ai/api/v1"
export API_KEY_ENV_NAME="OPENROUTER_API_KEY"

python -m proverb.commands.evaluate_openai --config configs/default.yaml \
  --task_type gen_eng_literal \
  --output_dir outputs/gpt-5-mini/gpt-5-mini-gen-eng-literal-Kenya \
  --model_name_or_path openai/gpt-5-chat \
  --template_name=none \
  --location=Kenya \
  --language=digo,ekegusii,gikuyu,kamba,luo,maasai,meru,nandi,nubian_2,nubian,nyala,olusamia,orma,rendille,samburu,teso,tugen,turkana \
  --api_delay=1.0 \
  --api_semophore=8 \
  --api_url=$API_URL \
  --api_key_env_name=$API_KEY_ENV_NAME

python -m proverb.commands.evaluate_openai --config configs/default.yaml \
  --task_type gen_eng_fig \
  --output_dir outputs/gpt-5-mini/gpt-5-mini-gen-eng-fig-Kenya \
  --model_name_or_path openai/gpt-5-chat \
  --location=Kenya \
  --language=digo,ekegusii,gikuyu,kamba,luo,maasai,meru,nandi,nubian_2,nubian,nyala,olusamia,orma,rendille,samburu,teso,tugen,turkana \
  --template_name=none \
  --api_delay=1.0 \
  --api_semophore=8 \
  --api_url=$API_URL \
  --api_key_env_name=$API_KEY_ENV_NAME

python -m proverb.commands.evaluate_openai --config configs/default.yaml \
  --task_type gen_swa_literal \
  --output_dir outputs/gpt-5-mini/gpt-5-mini-gen-swa-literal-Kenya \
  --model_name_or_path openai/gpt-5-chat \
  --location=Kenya \
  --language=digo,ekegusii,gikuyu,kamba,luo,maasai,meru,nandi,nubian_2,nubian,nyala,olusamia,orma,rendille,samburu,teso,tugen,turkana \
  --template_name=none \
  --api_delay=1.0 \
  --api_semophore=8 \
  --api_url=$API_URL \
  --api_key_env_name=$API_KEY_ENV_NAME

python -m proverb.commands.evaluate_openai --config configs/default.yaml \
  --task_type gen_swa_fig \
  --output_dir outputs/gpt-5-mini/gpt-5-mini-gen-swa-fig-Kenya \
  --model_name_or_path openai/gpt-5-chat \
  --location=Kenya \
  --language=digo,ekegusii,gikuyu,kamba,luo,maasai,meru,nandi,nubian_2,nubian,nyala,olusamia,orma,rendille,samburu,teso,tugen,turkana \
  --template_name=none \
  --api_delay=1.0 \
  --api_semophore=8 \
  --api_url=$API_URL \
  --api_key_env_name=$API_KEY_ENV_NAME

# Tanzania -----------------------------------------------------------------------------------------------------

python -m proverb.commands.evaluate_openai --config configs/default.yaml \
  --task_type gen_eng_literal \
  --output_dir outputs/gpt-5-mini/gpt-5-mini-gen-eng-literal-Tanzania \
  --model_name_or_path openai/gpt-5-chat \
  --template_name=none \
  --location=Tanzania \
  --language=gweno,kihangaza,kihara,makonde,nyaturu,pare,sukuma,zigula \
  --api_delay=1.0 \
  --api_semophore=8 \
  --api_url=$API_URL \
  --api_key_env_name=$API_KEY_ENV_NAME

python -m proverb.commands.evaluate_openai --config configs/default.yaml \
  --task_type gen_eng_fig \
  --output_dir outputs/gpt-5-mini/gpt-5-mini-gen-eng-fig-Tanzania \
  --model_name_or_path openai/gpt-5-chat \
  --template_name=none \
  --location=Tanzania \
  --language=gweno,kihangaza,kihara,makonde,nyaturu,pare,sukuma,zigula \
  --api_delay=1.0 \
  --api_semophore=8 \
  --api_url=$API_URL \
  --api_key_env_name=$API_KEY_ENV_NAME

python -m proverb.commands.evaluate_openai --config configs/default.yaml \
  --task_type gen_swa_literal \
  --output_dir outputs/gpt-5-mini/gpt-5-mini-gen-swa-literal-Tanzania \
  --model_name_or_path openai/gpt-5-chat \
  --location=Tanzania \
  --language=gweno,kihangaza,kihara,makonde,nyaturu,pare,sukuma,zigula \
  --template_name=none \
  --api_delay=1.0 \
  --api_semophore=8 \
  --api_url=$API_URL \
  --api_key_env_name=$API_KEY_ENV_NAME

python -m proverb.commands.evaluate_openai --config configs/default.yaml \
  --task_type gen_swa_fig \
  --output_dir outputs/gpt-5-mini/gpt-5-mini-gen-swa-fig-Tanzania \
  --model_name_or_path openai/gpt-5-chat \
  --location=Tanzania \
  --language=gweno,kihangaza,kihara,makonde,nyaturu,pare,sukuma,zigula \
  --template_name=none \
  --api_delay=1.0 \
  --api_semophore=8 \
  --api_url=$API_URL \
  --api_key_env_name=$API_KEY_ENV_NAME

# --- DRC

python -m proverb.commands.evaluate_openai --config configs/default.yaml \
  --task_type gen_eng_literal \
  --output_dir outputs/gpt-5-mini/gpt-5-mini-gen-eng-literal-DRC \
  --model_name_or_path openai/gpt-5-chat \
  --template_name=none \
  --location=DRC \
  --language=kwele,tetela,bangubangu,hema,hemba,holoholo,nande,taabwa,tshiluba \
  --api_delay=1.0 \
  --api_semophore=8 \
  --api_url=$API_URL \
  --api_key_env_name=$API_KEY_ENV_NAME

python -m proverb.commands.evaluate_openai --config configs/default.yaml \
  --task_type gen_eng_fig \
  --output_dir outputs/gpt-5-mini/gpt-5-mini-gen-eng-fig-DRC \
  --model_name_or_path openai/gpt-5-chat \
  --template_name=none \
  --location=DRC \
  --language=kwele,tetela,bangubangu,hema,hemba,holoholo,nande,taabwa,tshiluba \
  --api_delay=1.0 \
  --api_semophore=8 \
  --api_url=$API_URL \
  --api_key_env_name=$API_KEY_ENV_NAME

python -m proverb.commands.evaluate_openai --config configs/default.yaml \
  --task_type gen_swa_literal \
  --output_dir outputs/gpt-5-mini/gpt-5-mini-gen-swa-literal-DRC \
  --model_name_or_path openai/gpt-5-chat \
  --location=DRC \
  --language=kwele,tetela,bangubangu,hema,hemba,holoholo,nande,taabwa,tshiluba \
  --template_name=none \
  --api_delay=1.0 \
  --api_semophore=8 \
  --api_url=$API_URL \
  --api_key_env_name=$API_KEY_ENV_NAME

python -m proverb.commands.evaluate_openai --config configs/default.yaml \
  --task_type gen_swa_fig \
  --output_dir outputs/gpt-5-mini/gpt-5-mini-gen-swa-fig-DRC \
  --model_name_or_path openai/gpt-5-chat \
  --location=DRC \
  --language=kwele,tetela,bangubangu,hema,hemba,holoholo,nande,taabwa,tshiluba \
  --template_name=none \
  --api_delay=1.0 \
  --api_semophore=8 \
  --api_url=$API_URL \
  --api_key_env_name=$API_KEY_ENV_NAME

# Uganda
#
python -m proverb.commands.evaluate_openai --config configs/default.yaml \
  --task_type gen_eng_literal \
  --output_dir outputs/gpt-5-mini/gpt-5-mini-gen-eng-literal-Uganda \
  --model_name_or_path openai/gpt-5-chat \
  --template_name=none \
  --location=Uganda \
  --language=alur,chiga,ganda,rufumbira,runyoro,soga,tooro \
  --api_delay=1.0 \
  --api_semophore=8 \
  --api_url=$API_URL \
  --api_key_env_name=$API_KEY_ENV_NAME

python -m proverb.commands.evaluate_openai --config configs/default.yaml \
  --task_type gen_eng_fig \
  --output_dir outputs/gpt-5-mini/gpt-5-mini-gen-eng-fig-Uganda \
  --model_name_or_path openai/gpt-5-chat \
  --template_name=none \
  --location=Uganda \
  --language=alur,chiga,ganda,rufumbira,runyoro,soga,tooro \
  --api_delay=1.0 \
  --api_semophore=8 \
  --api_url=$API_URL \
  --api_key_env_name=$API_KEY_ENV_NAME

python -m proverb.commands.evaluate_openai --config configs/default.yaml \
  --task_type gen_swa_literal \
  --output_dir outputs/gpt-5-mini/gpt-5-mini-gen-swa-literal-Uganda \
  --model_name_or_path openai/gpt-5-chat \
  --location=Uganda \
  --language=alur,chiga,ganda,rufumbira,runyoro,soga,tooro \
  --template_name=none \
  --api_delay=1.0 \
  --api_semophore=8 \
  --api_url=$API_URL \
  --api_key_env_name=$API_KEY_ENV_NAME

python -m proverb.commands.evaluate_openai --config configs/default.yaml \
  --task_type gen_swa_fig \
  --output_dir outputs/gpt-5-mini/gpt-5-mini-gen-swa-fig-Uganda \
  --model_name_or_path openai/gpt-5-chat \
  --location=Uganda \
  --language=alur,chiga,ganda,rufumbira,runyoro,soga,tooro \
  --template_name=none \
  --api_delay=1.0 \
  --api_semophore=8 \
  --api_url=$API_URL \
  --api_key_env_name=$API_KEY_ENV_NAME

# Somali

python -m proverb.commands.evaluate_openai --config configs/default.yaml \
  --task_type gen_eng_literal \
  --output_dir outputs/gpt-5-mini/gpt-5-mini-gen-eng-literal-Somali \
  --model_name_or_path openai/gpt-5-chat \
  --template_name=none \
  --location=Somali \
  --language=Somali \
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
  --language=Somali \
  --api_delay=1.0 \
  --api_semophore=8 \
  --api_url=$API_URL \
  --api_key_env_name=$API_KEY_ENV_NAME

python -m proverb.commands.evaluate_openai --config configs/default.yaml \
  --task_type gen_swa_literal \
  --output_dir outputs/gpt-5-mini/gpt-5-mini-gen-swa-literal-Somali \
  --model_name_or_path openai/gpt-5-chat \
  --location=Somali \
  --language=Somali \
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
  --language=Somali \
  --template_name=none \
  --api_delay=1.0 \
  --api_semophore=8 \
  --api_url=$API_URL \
  --api_key_env_name=$API_KEY_ENV_NAME

# Ethiopia
#
python -m proverb.commands.evaluate_openai --config configs/default.yaml \
  --task_type gen_eng_literal \
  --output_dir outputs/gpt-5-mini/gpt-5-mini-gen-eng-literal-Ethiopia \
  --model_name_or_path openai/gpt-5-chat \
  --template_name=none \
  --location=Ethiopia \
  --language=borana,burji \
  --api_delay=1.0 \
  --api_semophore=8 \
  --api_url=$API_URL \
  --api_key_env_name=$API_KEY_ENV_NAME

python -m proverb.commands.evaluate_openai --config configs/default.yaml \
  --task_type gen_eng_fig \
  --output_dir outputs/gpt-5-mini/gpt-5-mini-gen-eng-fig-Ethiopia \
  --model_name_or_path openai/gpt-5-chat \
  --template_name=none \
  --location=Ethiopia \
  --language=borana,burji \
  --api_delay=1.0 \
  --api_semophore=8 \
  --api_url=$API_URL \
  --api_key_env_name=$API_KEY_ENV_NAME

python -m proverb.commands.evaluate_openai --config configs/default.yaml \
  --task_type gen_swa_literal \
  --output_dir outputs/gpt-5-mini/gpt-5-mini-gen-swa-literal-Ethiopia \
  --model_name_or_path openai/gpt-5-chat \
  --location=Ethiopia \
  --language=borana,burji \
  --template_name=none \
  --api_delay=1.0 \
  --api_semophore=8 \
  --api_url=$API_URL \
  --api_key_env_name=$API_KEY_ENV_NAME

python -m proverb.commands.evaluate_openai --config configs/default.yaml \
  --task_type gen_swa_fig \
  --output_dir outputs/gpt-5-mini/gpt-5-mini-gen-swa-fig-Ethiopia \
  --model_name_or_path openai/gpt-5-chat \
  --location=Ethiopia \
  --language=borana,burji \
  --template_name=none \
  --api_delay=1.0 \
  --api_semophore=8 \
  --api_url=$API_URL \
  --api_key_env_name=$API_KEY_ENV_NAME
