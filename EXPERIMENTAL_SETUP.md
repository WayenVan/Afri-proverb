# AfriProverb — Experimental Setup

## 1. Overview

This experiment evaluates how well large language models (LLMs) can translate and interpret African proverbs from 45 low-resource languages across 6 East/Central African countries. The project spans two repositories:

- **African-Proverbs/** — Dataset curation: 8,415 proverbs from 6 countries (Kenya, Tanzania, DRC, Uganda, Somali, Ethiopia) in 45 languages, stored as CSV files with columns for the original proverb, English literal translation, Swahili literal translation, and English figurative meaning.
- **Afri-proverb/** — Evaluation codebase: model inference, prompt engineering, metric computation, and Modal GPU orchestration.

## 2. Data Preparation

### 2.1 Dataset Collection

Proverbs were collected per country and language, each stored as `{language}_prov.csv` under `African-Proverbs/Data/{Country}/`. Every entry contains:

| Column | Description |
|--------|-------------|
| proverb | Original proverb in the source African language |
| eng_literal | Word-for-word English translation |
| swa_literal | Word-for-word Swahili translation |
| eng_figurative | Figurative/metaphorical English meaning |

### 2.2 Coverage

| Country | Languages | Proverbs |
|---------|-----------|----------|
| Kenya | 18 | 4,904 |
| Tanzania | 8 | 1,203 |
| DRC | 9 | 908 |
| Uganda | 7 | 700 |
| Somali | 1 | 500 |
| Ethiopia | 2 | 200 |
| **Total** | **45** | **8,415** |

### 2.3 Data Loading

The loader (`src/proverb/data/loader.py`) reads each CSV, converts it to a HuggingFace Dataset, and applies a Processor that tokenizes the proverb with the appropriate prompt template for the target model and task.

## 3. Task Definitions

Each model is evaluated on 4 translation/interpretation tasks:

| Task ID | Source | Target | Type |
|---------|--------|--------|------|
| `gen_eng_literal` | African language proverb | English | Literal translation |
| `gen_eng_fig` | African language proverb | English | Figurative meaning |
| `gen_swa_literal` | African language proverb | Swahili | Literal translation |
| `gen_swa_fig` | African language proverb | Swahili | Figurative meaning |

For each task, a structured prompt instructs the model on what kind of output is expected (literal vs. figurative), with explicit constraints (e.g., "preserve imagery", "avoid interpretation" for literal; "remove metaphor", "use plain language" for figurative).

Few-shot variants load language-specific example prompts from `few_shot_prompts/{Country}/{language}/`.

## 4. Models Evaluated

### 4.1 Local GPU Models (via HuggingFace + Accelerate or Modal)

| Model | Short Name | Template | Parameters |
|-------|-----------|----------|------------|
| google/gemma-3-1b-it | gemma3-1b-it | gemma | ~1B |
| google/gemma-3-4b-it | gemma3-4b-it | gemma | ~4B |
| google/gemma-3-12b-it | gemma3-12b-it | gemma | ~12B |
| meta-llama/Llama-3.2-3B-Instruct | llama3.2-3b | llama3 | ~3B |
| Qwen/Qwen3-4B | qwen3-4b | qwen3 | ~4B |
| HuggingFaceTB/SmolLM3-3B | smollm3-3b | smollm3 | ~3B |
| mistralai/Ministral-3-8B-Instruct-2512 | mistral-7b | mistral | ~8B |

### 4.2 API-Based Models (via OpenRouter)

| Model | Short Name |
|-------|-----------|
| moonshotai/kimi-k2.5 | kimi-k2 |

API models use `evaluate_openai.py` with async parallel requests (semaphore-controlled concurrency, configurable rate delay).

## 5. Infrastructure & Modal Setup

### 5.1 Why Modal

Local GPUs may be insufficient for running all 24 combinations (6 locations × 4 tasks) per model. Modal provides on-demand A100 GPUs with persistent volume storage.

### 5.2 Modal Container Image

All Modal scripts (`modal_gpu.py`, `modal_gemma.py`, `modal_llama.py`, `modal_smollm.py`) build the same Debian Slim + Python 3.10 image with:
- torch, transformers, accelerate, trl
- unbabel-comet 2.2.2
- datasets, evaluate, sacrebleu, rouge-score, pyyaml

### 5.3 Modal Execution Flow

1. Authenticate: `modal token new`
2. Upload code to Modal volume:
   ```
   modal volume put afri-proverb-data ./Afri-proverb /workspace/Afri-proverb
   modal volume put afri-proverb-data ./African-Proverbs /workspace/African-Proverbs
   ```
3. Run evaluation (e.g., Gemma): `modal run modal_gemma.py`
4. The script:
   - Symlinks the dataset directory
   - Iterates over all 6 locations × 4 tasks = 24 runs
   - Calls `python -m proverb.commands.evaluate` for each combination
   - Commits results to the Modal volume after each task
5. Download results: `modal volume get afri-proverb-data /workspace/outputs ./outputs`

### 5.4 Local Execution (Alternative)

For machines with local GPUs, shell scripts use Accelerate:
```bash
export PYTHONPATH="./src:$PYTHONPATH"
accelerate launch --num_processes=2 --mixed_precision=bf16 \
  -m proverb.commands.evaluate --config configs/default.yaml \
  --task_type gen_eng_literal \
  --output_dir outputs/gemma3-4b-it-gen-eng-literal-Kenya \
  --model_name_or_path google/gemma-3-4b-it
```

## 6. Evaluation Pipeline

### 6.1 Inference

The `evaluate.py` command:
1. Parses args from YAML config + CLI overrides
2. Loads tokenizer and model
3. Loads and tokenizes the proverb dataset per location/language
4. Runs `trainer.predict()` using a CustomTrainer (Seq2Seq)
5. Saves per-language prediction JSONL files

### 6.2 Metrics

Computed in `TranslateMetric` (for local models) and `metrics()` (for API models):

| Metric | Library | What It Measures |
|--------|---------|-----------------|
| BLEU | sacrebleu | N-gram overlap with reference |
| chrF | evaluate (chrf) | Character n-gram F-score |
| chrF++ | evaluate (chrf, word_order=2) | chrF with word bigrams |
| COMET | unbabel-comet | Neural MT quality (source-aware) |

### 6.3 Output Structure

```
outputs/{model_short}/{model_short}-{task_type}-{location}/
├── evaluation_results.json          # Aggregated metrics per language
└── generated_predictions_{loc}_{lang}.jsonl  # Per-sample predictions
```

Each JSONL line contains: `{"prompt": ..., "predict": ..., "label": ...}`

## 7. Experiment Matrix

Total evaluation runs per model: **6 locations × 4 tasks = 24 runs**
Total languages evaluated per run: varies by location (Kenya=18, Tanzania=8, DRC=9, Uganda=7, Somali=1, Ethiopia=2)

Full matrix: **7+ models × 4 tasks × 45 languages = 1,260+ individual language-task evaluations**

## 8. Reproducibility

- Config: `Afri-proverb/configs/default.yaml` stores default model, location, language, task, and training hyperparameters
- All Modal scripts are deterministic given the same volume state
- HuggingFace secrets are stored as Modal secrets (`huggingface-secret`)
- API keys are stored as environment variables (`OPENROUTER_API_KEY`)
- Results are persisted to Modal volumes and can be downloaded with `download_outputs.py`
