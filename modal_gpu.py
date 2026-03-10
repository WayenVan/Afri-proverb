"""
Modal GPU Environment for Afri-Proverb Evaluation

This creates a Modal container with GPU that you can:
1. SSH into to run commands interactively
2. Upload your code to and run evaluations
"""
import modal

app = modal.App("afri-proverb-gpu")

image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install("git", "rsync")
    .pip_install("setuptools")
    .pip_install(
        "torch",
        "transformers",
        "accelerate",
        "trl",
    )
    .pip_install(
        "unbabel-comet==2.2.2",
    )
    .pip_install(
        "datasets",
        "evaluate",
        "sacrebleu",
        "rouge-score",
        "pyyaml",
    )
)

volume = modal.Volume.from_name("afri-proverb-data", create_if_missing=True)

@app.function(
    image=image,
    gpu="A100",
    timeout=3600 * 12,
    volumes={"/workspace": volume},
)
def setup_and_run():
    """
    Run this to get a shell in the Modal container.
    Then you can rsync your code and run evaluations.
    """
    import subprocess
    import os
    
    os.chdir("/workspace")
    
    print("=" * 80)
    print("Modal GPU Environment Ready!")
    print("=" * 80)
    print("\nTo upload your code from your local machine, run:")
    print("\n  modal volume put afri-proverb-data /home/obote/Documents/SE/AOB/2026/NaomEtori/Afri-proverb /workspace/Afri-proverb")
    print("  modal volume put afri-proverb-data /home/obote/Documents/SE/AOB/2026/NaomEtori/African-Proverbs /workspace/African-Proverbs")
    print("\nThen run evaluations with:")
    print("\n  modal run modal_gpu.py::run_evaluations")
    print("=" * 80)
    
    # Keep container alive
    subprocess.run(["sleep", "43200"])  # 12 hours

@app.function(
    image=image,
    gpu="A100", 
    timeout=3600 * 12,
    volumes={"/workspace": volume},
    secrets=[modal.Secret.from_name("huggingface-secret")],
)
def run_evaluations():
    """Run all evaluations after code is uploaded"""
    import subprocess
    import os
    
    os.chdir("/workspace/workspace/Afri-proverb")
    os.environ["PYTHONPATH"] = "/workspace/workspace/Afri-proverb/src"
    
    # Create symlink for dataset
    if not os.path.exists("dataset"):
        os.makedirs("dataset", exist_ok=True)
        os.symlink("/workspace/workspace/African-Proverbs", "dataset/African-Proverbs", target_is_directory=True)
    
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
            output_dir = f"/workspace/outputs/{model_short}/{model_short}-{task_type}-{location}"
            os.makedirs(output_dir, exist_ok=True)
            
            print(f"\n{'='*80}")
            print(f"Running: {location} - {task_type}")
            print(f"{'='*80}\n")
            
            cmd = [
                "python", "-m", "proverb.commands.evaluate",
                "--config", "configs/default.yaml",
                "--task_type", task_type,
                "--output_dir", output_dir,
                "--template_name", template_name,
                "--model_name_or_path", model_name,
                "--location", location,
                "--language", language,
            ]
            
            result = subprocess.run(cmd)
            
            # Commit volume after each task to save results incrementally
            volume.commit()
            
            if result.returncode == 0:
                print(f"✓ Completed: {location} - {task_type}")
            else:
                print(f"✗ Failed: {location} - {task_type}")
    
    print("\nAll evaluations completed!")
    volume.commit()
    print("Results saved to volume!")
    print("Download results with:")
    print("  modal volume get afri-proverb-data /workspace/outputs ./outputs")

if __name__ == "__main__":
    print(__doc__)
