import modal
import os

stub = modal.Stub("afri-proverb-eval")

image = modal.Image.debian_slim(python_version="3.10").pip_install(
    "torch",
    "transformers", 
    "accelerate",
    "datasets",
    "evaluate",
    "sacrebleu",
    "rouge-score",
    "pyyaml",
)

volume = modal.NetworkFileSystem.persisted("afri-proverb-outputs")

@stub.function(
    image=image,
    gpu="A100",
    timeout=3600 * 6,
    network_file_systems={"/outputs": volume},
)
def run_evaluation(location, language, task_type, model_name, template_name, model_short):
    import subprocess
    import sys
    
    # Write code files
    os.makedirs("/root/src/proverb", exist_ok=True)
    os.makedirs("/root/configs", exist_ok=True)
    
    # Copy files from local context
    import shutil
    for root, dirs, files in os.walk("/root"):
        for file in files:
            if file.endswith(".py"):
                print(f"Found: {os.path.join(root, file)}")
    
    sys.path.insert(0, "/root/src")
    os.environ["PYTHONPATH"] = "/root/src"
    
    output_dir = f"/outputs/{model_short}/{model_short}-{task_type}-{location}"
    os.makedirs(output_dir, exist_ok=True)
    
    cmd = [
        "python", "-m", "proverb.commands.evaluate",
        "--config", "/root/configs/default.yaml",
        "--task_type", task_type,
        "--output_dir", output_dir,
        "--template_name", template_name,
        "--model_name_or_path", model_name,
        "--location", location,
        "--language", language,
    ]
    
    print(f"Running: Location={location}, Task={task_type}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print(f"Return code: {result.returncode}")
    if result.stdout:
        print(f"STDOUT:\n{result.stdout[-1000:]}")
    if result.stderr:
        print(f"STDERR:\n{result.stderr[-1000:]}")
    
    return {
        "location": location,
        "task_type": task_type,
        "returncode": result.returncode,
        "success": result.returncode == 0,
    }

@stub.local_entrypoint()
def main():
    locations = {
        "Kenya": "digo, ekegusii, gikuyu, kamba, luo, maasai, meru, nandi, nubian_2, nubian, nyala, olusamia, orma, rendille, samburu, teso, tugen, turkana",
    }
    
    task_types = ["gen_eng_literal"]
    model_name = "Qwen/Qwen3-4B"
    model_short = "qwen3-4b"
    template_name = "qwen3"
    
    # Test with just one task first
    for location, language in locations.items():
        for task_type in task_types:
            result = run_evaluation.remote(
                location, language, task_type, model_name, template_name, model_short
            )
            print(f"Result: {result}")
    
    print("Test completed!")
