import modal
import os

app = modal.App("afri-proverb-eval")

image = (
    modal.Image.debian_slim(python_version="3.10")
    .pip_install(
        "torch",
        "transformers",
        "accelerate",
        "datasets",
        "evaluate",
        "sacrebleu",
        "rouge-score",
        "pyyaml",
    )
)

volume = modal.Volume.from_name("afri-proverb-outputs", create_if_missing=True)

@app.function(
    image=image,
    gpu="A100",
    timeout=3600 * 6,
    volumes={"/outputs": volume},
)
def run_evaluation(location, language, task_type, model_name, template_name, model_short):
    import subprocess
    
    os.environ["PYTHONPATH"] = "/root/src"
    
    output_dir = f"/outputs/{model_short}/{model_short}-{task_type}-{location}"
    os.makedirs(output_dir, exist_ok=True)
    
    cmd = [
        "accelerate", "launch",
        "--num_processes=1",
        "--mixed_precision=bf16",
        "-m", "proverb.commands.evaluate",
        "--config", "/root/configs/default.yaml",
        "--task_type", task_type,
        "--output_dir", output_dir,
        "--template_name", template_name,
        "--model_name_or_path", model_name,
        "--location", location,
        "--language", language,
    ]
    
    print(f"Running: Location={location}, Task={task_type}")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd="/root")
    
    print(f"STDOUT:\n{result.stdout}")
    if result.stderr:
        print(f"STDERR:\n{result.stderr}")
    
    volume.commit()
    
    return {
        "location": location,
        "task_type": task_type,
        "returncode": result.returncode,
        "success": result.returncode == 0,
    }

@app.local_entrypoint()
def main():
    locations = {
        "Kenya": "digo, ekegusii, gikuyu, kamba, luo, maasai, meru, nandi, nubian_2, nubian, nyala, olusamia, orma, rendille, samburu, teso, tugen, turkana",
        "Tanzania": "gweno, kihangaza, kihara, makonde, nyaturu, pare, sukuma, zigula",
        "DRC": "kwele, tetela, bangubangu, hema, hemba, holoholo, nande, taabwa, tshiluba",
        "Uganda": "alur, chiga, ganda, rufumbira, runyoro, soga, tooro",
        "Somali": "somali",
        "Ethiopia": "borana, burji",
    }
    
    task_types = ["gen_eng_literal", "gen_eng_fig", "gen_swa_literal", "gen_swa_fig"]
    model_name = "Qwen/Qwen3-4B"
    model_short = "qwen3-4b"
    template_name = "qwen3"
    
    for location, language in locations.items():
        for task_type in task_types:
            run_evaluation.remote(
                location, language, task_type, model_name, template_name, model_short
            )
            print(f"Submitted: {location} - {task_type}")
    
    print("All evaluations submitted!")
