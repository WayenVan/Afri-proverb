# Running Afri-Proverb Evaluation on Modal GPU

## Setup

1. **Activate conda environment:**
```bash
cd /home/obote/Documents/SE/AOB/2026/NaomEtori/Afri-proverb
conda activate audio_ml
```

2. **Authenticate Modal (if not done):**
```bash
modal token new
```

## Run Evaluation

**Run all locations and tasks:**
```bash
modal run modal_run.py
```

This will:
- Mount your local code to Modal
- Run on A100 GPU
- Execute all 24 combinations (6 locations × 4 tasks)
- Save results to Modal volume

## Monitor Progress

**View logs in real-time:**
- Check the Modal dashboard URL shown in terminal
- Or use: `modal app logs viviannyamoraa/main::afri-proverb-eval`

**Start Jupyter notebook locally:**
```bash
jupyter notebook monitor_evaluation.ipynb
```

## Download Results from Modal

**List volume contents:**
```bash
modal volume ls afri-proverb-outputs /outputs
```

**Download all results:**
```bash
modal volume get afri-proverb-outputs /outputs ./outputs
```

**Download specific location:**
```bash
modal volume get afri-proverb-outputs /outputs/qwen3-4b/qwen3-4b-gen-eng-literal-Kenya ./outputs/qwen3-4b/
```

## Notes

- Each evaluation runs sequentially on A100 GPU
- Timeout: 6 hours per task
- Results auto-saved to Modal volume after each task
- Volume persists between runs
- First run downloads model (~8GB for Qwen3-4B)
