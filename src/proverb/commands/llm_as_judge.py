import json
import os
import itertools
from typing import Dict, Any, List, Tuple
import time

import numpy as np
import pandas as pd
from openai import OpenAI

# ============================================================
# CONFIG
# ============================================================

INPUT_CSV = "outputs/all_results/smollm3-3b-it_all_results.csv"

# Row-level outputs
OUTPUT_SCORED_CSV = "outputs/llm_judge_scored.csv"
OUTPUT_PAIRWISE_CSV = "outputs/llm_judge_pairwise.csv"

# Final paper tables
OUTPUT_TABLE1_MAIN_RESULTS_CSV = "outputs/table1_main_results_mean_std.csv"
OUTPUT_TABLE2_MODEL_TASK_CSV = "outputs/table2_model_task_mean_std.csv"
OUTPUT_TABLE3_LANGUAGE_CSV = "outputs/table3_language_results_mean_std.csv"
OUTPUT_TABLE4_WINRATE_CSV = "outputs/table4_pairwise_win_rates.csv"

# Judge model
JUDGE_MODEL = "gpt-4.1-mini"

# Runtime behavior
SLEEP_BETWEEN_CALLS = 0.2
MAX_RETRIES = 3
RESUME_IF_OUTPUT_EXISTS = True

# Toggle this if you want true pairwise LLM judging for Table 4
# If False, Table 4 is derived from row-level overall scores
USE_LLM_FOR_PAIRWISE = True

# Preferred task order in paper tables
TASK_ORDER = ["eng_literal", "swa_literal", "eng_figurative", "swa_figurative"]

client = OpenAI(
    api_key=os.environ["OPENROUTER_API_KEY"], base_url="https://openrouter.ai/api/v1"
)


# ============================================================
# BASIC HELPERS
# ============================================================


def get_target_language(task: str) -> str:
    if task.startswith("eng_"):
        return "English"
    if task.startswith("swa_"):
        return "Swahili"
    return "Unknown"


def safe_std(series: pd.Series) -> float:
    std = series.std(ddof=1)
    if pd.isna(std):
        return 0.0
    return float(std)


def mean_std_str(series: pd.Series, decimals: int = 2) -> str:
    mean = float(series.mean())
    std = safe_std(series)
    return f"{mean:.{decimals}f} ± {std:.{decimals}f}"


def numeric_mean_from_mean_std(text: str) -> float:
    return float(str(text).split(" ± ")[0])


def extract_json(text: str) -> Dict[str, Any]:
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return json.loads(text[start : end + 1])

    raise ValueError(f"Could not parse JSON from response: {text}")


# ============================================================
# UID HELPERS
# ============================================================


def get_single_row_uid(row: pd.Series) -> str:
    return "|||".join(
        [
            str(row["proverb_id"]),
            str(row["language"]),
            str(row["task"]),
            str(row["model"]),
            str(row["source_proverb"]),
            str(row["reference"]),
            str(row["prediction"]),
        ]
    )


def get_pair_uid(
    proverb_id: Any,
    language: str,
    task: str,
    model_a: str,
    model_b: str,
    source_proverb: str,
    reference: str,
    prediction_a: str,
    prediction_b: str,
) -> str:
    return "|||".join(
        [
            str(proverb_id),
            str(language),
            str(task),
            str(model_a),
            str(model_b),
            str(source_proverb),
            str(reference),
            str(prediction_a),
            str(prediction_b),
        ]
    )


def attach_single_uid(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["row_uid"] = df.apply(get_single_row_uid, axis=1)
    return df


# ============================================================
# PROMPTS
# ============================================================


def build_single_judge_prompt(
    task_type: str,
    source_language: str,
    source_proverb: str,
    reference_text: str,
    candidate_output: str,
) -> str:
    target_language = get_target_language(task_type)

    return f"""
You are evaluating translations of African proverbs produced by different models.

Your goal is to assess the quality of one translation according to four evaluation criteria:
1. Meaning Accuracy
2. Adequacy
3. Fluency
4. Cultural Naturalness

Please evaluate the candidate translation independently and objectively.

Task type: {task_type}
Source language: {source_language}
Target language: {target_language}

Source proverb:
{source_proverb}

Reference label:
{reference_text}

Candidate translation:
{candidate_output}

Evaluation Criteria

1. Meaning Accuracy
Assess whether the translation correctly conveys the intended meaning or interpretation of the proverb.
- 5 = Meaning completely correct and fully captures the message.
- 4 = Mostly correct; minor nuance missing.
- 3 = Partially correct; meaning preserved but incomplete.
- 2 = Mostly incorrect interpretation.
- 1 = Completely incorrect meaning.

2. Adequacy
Measures whether the meaning of the source proverb is preserved.
- For literal translation: meaning and imagery preserved.
- For figurative translation: interpretation or moral preserved.
- 5 = All meaning preserved.
- 4 = Minor meaning loss.
- 3 = Partial preservation.
- 2 = Major meaning loss.
- 1 = Meaning missing or incorrect.

3. Fluency
Evaluate whether the translation is grammatically correct and natural.
- 5 = Perfectly fluent.
- 4 = Minor issues.
- 3 = Understandable but awkward.
- 2 = Difficult to read.
- 1 = Unintelligible.

4. Cultural Naturalness
Assess whether the translation sounds culturally appropriate as a proverb.
- 5 = Very natural proverb expression.
- 4 = Mostly natural.
- 3 = Neutral.
- 2 = Somewhat unnatural.
- 1 = Completely unnatural.

Important instructions:
- Use the reference label as the main anchor for correctness.
- If the output copies the source proverb instead of translating it, assign very low scores.
- If the output is fluent but semantically wrong, Fluency may be high, but Meaning Accuracy and Adequacy must remain low.
- If the output loses metaphor, imagery, or semantic content, penalize Meaning Accuracy and Adequacy.
- For literal tasks, reward preservation of imagery and entities.
- For figurative tasks, reward preservation of intended interpretation or moral.
- Judge only the candidate translation shown above.

Return ONLY valid JSON in this format:
{{
  "meaning_accuracy": <integer 1-5>,
  "adequacy": <integer 1-5>,
  "fluency": <integer 1-5>,
  "cultural_naturalness": <integer 1-5>,
  "short_reason": "<one short sentence>"
}}
""".strip()


def build_pairwise_judge_prompt(
    task_type: str,
    source_language: str,
    source_proverb: str,
    reference_text: str,
    candidate_a: str,
    candidate_b: str,
) -> str:
    target_language = get_target_language(task_type)

    return f"""
You are evaluating translations of African proverbs produced by different models.

Your goal is to compare two candidate translations and decide which one is better overall.

Please use the following evaluation criteria:
1. Meaning Accuracy
2. Adequacy
3. Fluency
4. Cultural Naturalness

Task type: {task_type}
Source language: {source_language}
Target language: {target_language}

Source proverb:
{source_proverb}

Reference label:
{reference_text}

Model A translation:
{candidate_a}

Model B translation:
{candidate_b}

Evaluation Criteria

1. Meaning Accuracy
Assess whether the translation correctly conveys the intended meaning or interpretation of the proverb.
- 5 = Meaning completely correct and fully captures the message.
- 4 = Mostly correct; minor nuance missing.
- 3 = Partially correct; meaning preserved but incomplete.
- 2 = Mostly incorrect interpretation.
- 1 = Completely incorrect meaning.

2. Adequacy
Measures whether the meaning of the source proverb is preserved.
- For literal translation: meaning and imagery preserved.
- For figurative translation: interpretation or moral preserved.
- 5 = All meaning preserved.
- 4 = Minor meaning loss.
- 3 = Partial preservation.
- 2 = Major meaning loss.
- 1 = Meaning missing or incorrect.

3. Fluency
Evaluate whether the translation is grammatically correct and natural.
- 5 = Perfectly fluent.
- 4 = Minor issues.
- 3 = Understandable but awkward.
- 2 = Difficult to read.
- 1 = Unintelligible.

4. Cultural Naturalness
Assess whether the translation sounds culturally appropriate as a proverb.
- 5 = Very natural proverb expression.
- 4 = Mostly natural.
- 3 = Neutral.
- 2 = Somewhat unnatural.
- 1 = Completely unnatural.

Pairwise decision:
- Choose Model A if A is better overall.
- Choose Model B if B is better overall.
- Choose Tie if both are equally good or equally poor.

Important instructions:
- Use the reference label as the main anchor for correctness.
- If one output copies the source and the other attempts a translation, prefer the translation attempt.
- If both outputs are equally poor, choose Tie.
- Meaning Accuracy and Adequacy are more important than Fluency when deciding the better translation.

Return ONLY valid JSON in this format:
{{
  "A": {{
    "meaning_accuracy": <integer 1-5>,
    "adequacy": <integer 1-5>,
    "fluency": <integer 1-5>,
    "cultural_naturalness": <integer 1-5>
  }},
  "B": {{
    "meaning_accuracy": <integer 1-5>,
    "adequacy": <integer 1-5>,
    "fluency": <integer 1-5>,
    "cultural_naturalness": <integer 1-5>
  }},
  "winner": "A|B|Tie",
  "short_reason": "<one short sentence>"
}}
""".strip()


# ============================================================
# API CALLS
# ============================================================


def judge_single(prompt: str) -> Dict[str, Any]:
    for attempt in range(MAX_RETRIES):
        try:
            response = client.responses.create(
                model=JUDGE_MODEL,
                temperature=0,
                input=prompt,
            )
            data = extract_json(response.output_text)

            required = {
                "meaning_accuracy",
                "adequacy",
                "fluency",
                "cultural_naturalness",
                "short_reason",
            }
            missing = required - set(data.keys())
            if missing:
                raise ValueError(f"Missing keys in single-judge output: {missing}")

            for key in [
                "meaning_accuracy",
                "adequacy",
                "fluency",
                "cultural_naturalness",
            ]:
                value = data[key]
                if not isinstance(value, int) or not (1 <= value <= 5):
                    raise ValueError(f"{key} must be integer 1-5, got {value}")

            return data

        except Exception as e:
            if attempt == MAX_RETRIES - 1:
                raise RuntimeError(
                    f"Single judge failed after {MAX_RETRIES} attempts: {e}"
                ) from e
            time.sleep(1.5 * (attempt + 1))

    raise RuntimeError("Unexpected failure in judge_single")


def judge_pairwise(prompt: str) -> Dict[str, Any]:
    for attempt in range(MAX_RETRIES):
        try:
            response = client.responses.create(
                model=JUDGE_MODEL,
                temperature=0,
                input=prompt,
            )
            data = extract_json(response.output_text)

            required = {"A", "B", "winner", "short_reason"}
            missing = required - set(data.keys())
            if missing:
                raise ValueError(f"Missing keys in pairwise output: {missing}")

            for side in ["A", "B"]:
                sub = data[side]
                for key in [
                    "meaning_accuracy",
                    "adequacy",
                    "fluency",
                    "cultural_naturalness",
                ]:
                    value = sub[key]
                    if not isinstance(value, int) or not (1 <= value <= 5):
                        raise ValueError(
                            f"{side}.{key} must be integer 1-5, got {value}"
                        )

            if data["winner"] not in {"A", "B", "Tie"}:
                raise ValueError(f"winner must be A, B, or Tie; got {data['winner']}")

            return data

        except Exception as e:
            if attempt == MAX_RETRIES - 1:
                raise RuntimeError(
                    f"Pairwise judge failed after {MAX_RETRIES} attempts: {e}"
                ) from e
            time.sleep(1.5 * (attempt + 1))

    raise RuntimeError("Unexpected failure in judge_pairwise")


# ============================================================
# SINGLE-OUTPUT SCORING
# ============================================================


def score_predictions(df: pd.DataFrame) -> pd.DataFrame:
    df = attach_single_uid(df)
    results: List[Dict[str, Any]] = []

    already_done = set()
    if RESUME_IF_OUTPUT_EXISTS and os.path.exists(OUTPUT_SCORED_CSV):
        prev = pd.read_csv(OUTPUT_SCORED_CSV)
        if "row_uid" in prev.columns:
            already_done = set(prev["row_uid"].astype(str).tolist())
            results.extend(prev.to_dict(orient="records"))
            print(f"Loaded {len(already_done)} previously scored rows")

    rows_to_score = df[~df["row_uid"].isin(already_done)].reset_index(drop=True)
    print(f"Need to score {len(rows_to_score)} new rows")

    for idx, row in rows_to_score.iterrows():
        prompt = build_single_judge_prompt(
            task_type=str(row["task"]),
            source_language=str(row["language"]),
            source_proverb=str(row["source_proverb"]),
            reference_text=str(row["reference"]),
            candidate_output=str(row["prediction"]),
        )

        out = judge_single(prompt)

        meaning = out["meaning_accuracy"]
        adequacy = out["adequacy"]
        fluency = out["fluency"]
        cultural = out["cultural_naturalness"]
        overall = (meaning + adequacy + fluency + cultural) / 4.0

        out_row = row.to_dict()
        out_row.update(
            {
                "meaning_accuracy": meaning,
                "adequacy": adequacy,
                "fluency": fluency,
                "cultural_naturalness": cultural,
                "overall": overall,
                "judge_reason": out["short_reason"],
            }
        )
        results.append(out_row)

        if (idx + 1) % 25 == 0 or (idx + 1) == len(rows_to_score):
            pd.DataFrame(results).to_csv(OUTPUT_SCORED_CSV, index=False)
            print(f"Scored {idx + 1}/{len(rows_to_score)} new rows")

        time.sleep(SLEEP_BETWEEN_CALLS)

    scored_df = pd.DataFrame(results)
    scored_df = scored_df.drop_duplicates(subset=["row_uid"], keep="last").reset_index(
        drop=True
    )
    return scored_df


# ============================================================
# TABLE HELPERS
# ============================================================


def build_mean_std_table(
    df: pd.DataFrame, group_cols: List[str], metrics: List[str]
) -> pd.DataFrame:
    rows = []
    for group_name, g in df.groupby(group_cols, dropna=False):
        if not isinstance(group_name, tuple):
            group_name = (group_name,)
        row = {}
        for col_name, value in zip(group_cols, group_name):
            row[col_name] = value
        for metric in metrics:
            row[metric] = mean_std_str(g[metric])
        rows.append(row)
    return pd.DataFrame(rows)


# ============================================================
# TABLE 1
# ============================================================


def make_table1_main_results(scored_df: pd.DataFrame) -> pd.DataFrame:
    metrics = [
        "meaning_accuracy",
        "adequacy",
        "fluency",
        "cultural_naturalness",
        "overall",
    ]
    table = build_mean_std_table(scored_df, ["model"], metrics)

    table = table.rename(
        columns={
            "model": "Model",
            "meaning_accuracy": "Meaning",
            "adequacy": "Adequacy",
            "fluency": "Fluency",
            "cultural_naturalness": "Cultural",
            "overall": "Overall",
        }
    )

    table["_sort"] = table["Overall"].apply(numeric_mean_from_mean_std)
    table = (
        table.sort_values("_sort", ascending=False)
        .drop(columns="_sort")
        .reset_index(drop=True)
    )
    return table


# ============================================================
# TABLE 2
# ============================================================


def make_table2_model_task(scored_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (model, task), g in scored_df.groupby(["model", "task"], dropna=False):
        rows.append(
            {
                "Model": model,
                "task": task,
                "value": mean_std_str(g["overall"]),
            }
        )

    long_df = pd.DataFrame(rows)
    pivot = long_df.pivot(index="Model", columns="task", values="value").reset_index()

    existing_tasks = list(long_df["task"].unique())
    ordered_tasks = [t for t in TASK_ORDER if t in existing_tasks] + [
        t for t in existing_tasks if t not in TASK_ORDER
    ]

    for t in ordered_tasks:
        if t not in pivot.columns:
            pivot[t] = np.nan

    pivot = pivot[["Model"] + ordered_tasks]

    overall = (
        scored_df.groupby("model")["overall"]
        .apply(mean_std_str)
        .reset_index()
        .rename(columns={"model": "Model", "overall": "Overall"})
    )
    pivot = pivot.merge(overall, on="Model", how="left")

    pivot = pivot.rename(
        columns={
            "eng_literal": "ENG Literal",
            "swa_literal": "SWA Literal",
            "eng_figurative": "ENG Figurative",
            "swa_figurative": "SWA Figurative",
        }
    )

    pivot["_sort"] = pivot["Overall"].apply(numeric_mean_from_mean_std)
    pivot = (
        pivot.sort_values("_sort", ascending=False)
        .drop(columns="_sort")
        .reset_index(drop=True)
    )
    return pivot


# ============================================================
# TABLE 3
# ============================================================


def make_table3_language(scored_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (language, model), g in scored_df.groupby(["language", "model"], dropna=False):
        rows.append(
            {
                "Language": language,
                "Model": model,
                "value": mean_std_str(g["overall"]),
            }
        )

    long_df = pd.DataFrame(rows)
    pivot = long_df.pivot(
        index="Language", columns="Model", values="value"
    ).reset_index()

    def row_best_mean(row: pd.Series) -> float:
        vals = []
        for col in row.index:
            if col == "Language" or pd.isna(row[col]):
                continue
            vals.append(numeric_mean_from_mean_std(row[col]))
        return max(vals) if vals else -np.inf

    pivot["_sort"] = pivot.apply(row_best_mean, axis=1)
    pivot = (
        pivot.sort_values("_sort", ascending=False)
        .drop(columns="_sort")
        .reset_index(drop=True)
    )
    return pivot


# ============================================================
# PAIRWISE GENERATION
# ============================================================


def generate_pairwise_input(scored_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build all model pairs within each proverb/language/task.
    """
    records = []

    grouped = scored_df.groupby(["proverb_id", "language", "task"], dropna=False)
    for (proverb_id, language, task), g in grouped:
        g = g.sort_values("model").reset_index(drop=True)

        # Need at least 2 models to compare
        if len(g) < 2:
            continue

        for i, j in itertools.combinations(range(len(g)), 2):
            a = g.loc[i]
            b = g.loc[j]

            pair_uid = get_pair_uid(
                proverb_id=proverb_id,
                language=str(language),
                task=str(task),
                model_a=str(a["model"]),
                model_b=str(b["model"]),
                source_proverb=str(a["source_proverb"]),
                reference=str(a["reference"]),
                prediction_a=str(a["prediction"]),
                prediction_b=str(b["prediction"]),
            )

            records.append(
                {
                    "pair_uid": pair_uid,
                    "proverb_id": proverb_id,
                    "language": language,
                    "task": task,
                    "source_proverb": a["source_proverb"],
                    "reference": a["reference"],
                    "model_a": a["model"],
                    "model_b": b["model"],
                    "prediction_a": a["prediction"],
                    "prediction_b": b["prediction"],
                }
            )

    return pd.DataFrame(records)


# ============================================================
# PAIRWISE JUDGING
# ============================================================


def run_pairwise_judging(scored_df: pd.DataFrame) -> pd.DataFrame:
    pair_df = generate_pairwise_input(scored_df)
    if pair_df.empty:
        return pd.DataFrame()

    results: List[Dict[str, Any]] = []
    already_done = set()

    if RESUME_IF_OUTPUT_EXISTS and os.path.exists(OUTPUT_PAIRWISE_CSV):
        prev = pd.read_csv(OUTPUT_PAIRWISE_CSV)
        if "pair_uid" in prev.columns:
            already_done = set(prev["pair_uid"].astype(str).tolist())
            results.extend(prev.to_dict(orient="records"))
            print(f"Loaded {len(already_done)} previously judged pairwise rows")

    rows_to_score = pair_df[~pair_df["pair_uid"].isin(already_done)].reset_index(
        drop=True
    )
    print(f"Need to pairwise-score {len(rows_to_score)} new rows")

    for idx, row in rows_to_score.iterrows():
        prompt = build_pairwise_judge_prompt(
            task_type=str(row["task"]),
            source_language=str(row["language"]),
            source_proverb=str(row["source_proverb"]),
            reference_text=str(row["reference"]),
            candidate_a=str(row["prediction_a"]),
            candidate_b=str(row["prediction_b"]),
        )

        out = judge_pairwise(prompt)

        rec = row.to_dict()
        rec.update(
            {
                "A_meaning_accuracy": out["A"]["meaning_accuracy"],
                "A_adequacy": out["A"]["adequacy"],
                "A_fluency": out["A"]["fluency"],
                "A_cultural_naturalness": out["A"]["cultural_naturalness"],
                "B_meaning_accuracy": out["B"]["meaning_accuracy"],
                "B_adequacy": out["B"]["adequacy"],
                "B_fluency": out["B"]["fluency"],
                "B_cultural_naturalness": out["B"]["cultural_naturalness"],
                "winner": out["winner"],
                "short_reason": out["short_reason"],
            }
        )
        results.append(rec)

        if (idx + 1) % 25 == 0 or (idx + 1) == len(rows_to_score):
            pd.DataFrame(results).to_csv(OUTPUT_PAIRWISE_CSV, index=False)
            print(f"Pairwise scored {idx + 1}/{len(rows_to_score)} new rows")

        time.sleep(SLEEP_BETWEEN_CALLS)

    out_df = pd.DataFrame(results)
    out_df = out_df.drop_duplicates(subset=["pair_uid"], keep="last").reset_index(
        drop=True
    )
    return out_df


# ============================================================
# TABLE 4
# ============================================================


def make_table4_from_pairwise_llm(pairwise_df: pd.DataFrame) -> pd.DataFrame:
    if pairwise_df.empty:
        return pd.DataFrame(
            columns=[
                "Comparison",
                "Model A",
                "Model B",
                "A Wins",
                "B Wins",
                "Ties",
                "Win Rate A (%)",
                "Win Rate B (%)",
            ]
        )

    rows = []
    for (model_a, model_b), g in pairwise_df.groupby(
        ["model_a", "model_b"], dropna=False
    ):
        a_wins = int((g["winner"] == "A").sum())
        b_wins = int((g["winner"] == "B").sum())
        ties = int((g["winner"] == "Tie").sum())

        denom = a_wins + b_wins
        win_rate_a = 100.0 * a_wins / denom if denom > 0 else np.nan
        win_rate_b = 100.0 * b_wins / denom if denom > 0 else np.nan

        rows.append(
            {
                "Comparison": f"{model_a} vs {model_b}",
                "Model A": model_a,
                "Model B": model_b,
                "A Wins": a_wins,
                "B Wins": b_wins,
                "Ties": ties,
                "Win Rate A (%)": round(win_rate_a, 2)
                if pd.notna(win_rate_a)
                else np.nan,
                "Win Rate B (%)": round(win_rate_b, 2)
                if pd.notna(win_rate_b)
                else np.nan,
            }
        )

    table = pd.DataFrame(rows)
    if not table.empty:
        table = table.sort_values(
            ["Win Rate A (%)", "A Wins"], ascending=[False, False]
        ).reset_index(drop=True)
    return table


def make_table4_from_overall_scores(scored_df: pd.DataFrame) -> pd.DataFrame:
    """
    Fallback if USE_LLM_FOR_PAIRWISE=False.
    """
    comparisons = []

    for _, g in scored_df.groupby(["proverb_id", "language", "task"], dropna=False):
        g = g[["model", "overall"]].dropna().sort_values("model").reset_index(drop=True)
        for i, j in itertools.combinations(range(len(g)), 2):
            model_a = g.loc[i, "model"]
            model_b = g.loc[j, "model"]
            score_a = g.loc[i, "overall"]
            score_b = g.loc[j, "overall"]

            if score_a > score_b:
                winner = "A"
            elif score_b > score_a:
                winner = "B"
            else:
                winner = "Tie"

            comparisons.append(
                {
                    "model_a": model_a,
                    "model_b": model_b,
                    "winner": winner,
                }
            )

    comp_df = pd.DataFrame(comparisons)
    if comp_df.empty:
        return pd.DataFrame()

    rows = []
    for (model_a, model_b), g in comp_df.groupby(["model_a", "model_b"], dropna=False):
        a_wins = int((g["winner"] == "A").sum())
        b_wins = int((g["winner"] == "B").sum())
        ties = int((g["winner"] == "Tie").sum())
        denom = a_wins + b_wins
        win_rate_a = 100.0 * a_wins / denom if denom > 0 else np.nan
        win_rate_b = 100.0 * b_wins / denom if denom > 0 else np.nan

        rows.append(
            {
                "Comparison": f"{model_a} vs {model_b}",
                "Model A": model_a,
                "Model B": model_b,
                "A Wins": a_wins,
                "B Wins": b_wins,
                "Ties": ties,
                "Win Rate A (%)": round(win_rate_a, 2)
                if pd.notna(win_rate_a)
                else np.nan,
                "Win Rate B (%)": round(win_rate_b, 2)
                if pd.notna(win_rate_b)
                else np.nan,
            }
        )

    table = pd.DataFrame(rows)
    if not table.empty:
        table = table.sort_values(
            ["Win Rate A (%)", "A Wins"], ascending=[False, False]
        ).reset_index(drop=True)
    return table


# ============================================================
# MAIN
# ============================================================


def main() -> None:
    df = pd.read_csv(INPUT_CSV)

    required_columns = {
        "proverb_id",
        "language",
        "task",
        "model",
        "source_proverb",
        "reference",
        "prediction",
    }
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"Input CSV is missing required columns: {missing}")

    print(f"Loaded {len(df)} rows from {INPUT_CSV}")

    # -------------------------
    # Step 1: single-output judging
    # -------------------------
    scored_df = score_predictions(df)
    scored_df.to_csv(OUTPUT_SCORED_CSV, index=False)
    print(f"Saved scored rows to {OUTPUT_SCORED_CSV}")

    # -------------------------
    # Step 2: Tables 1-3
    # -------------------------
    table1 = make_table1_main_results(scored_df)
    table2 = make_table2_model_task(scored_df)
    table3 = make_table3_language(scored_df)

    # # -------------------------
    # # Step 3: Table 4
    # # -------------------------
    # if USE_LLM_FOR_PAIRWISE:
    #     pairwise_df = run_pairwise_judging(scored_df)
    #     pairwise_df.to_csv(OUTPUT_PAIRWISE_CSV, index=False)
    #     print(f"Saved pairwise rows to {OUTPUT_PAIRWISE_CSV}")
    #     table4 = make_table4_from_pairwise_llm(pairwise_df)
    # else:
    #     table4 = make_table4_from_overall_scores(scored_df)
    #
    # -------------------------
    # Step 4: save final tables
    # -------------------------
    table1.to_csv(OUTPUT_TABLE1_MAIN_RESULTS_CSV, index=False)
    table2.to_csv(OUTPUT_TABLE2_MODEL_TASK_CSV, index=False)
    table3.to_csv(OUTPUT_TABLE3_LANGUAGE_CSV, index=False)
    # table4.to_csv(OUTPUT_TABLE4_WINRATE_CSV, index=False)

    # -------------------------
    # Step 5: preview
    # -------------------------
    print("\n=== TABLE 1: Main Results ===")
    print(table1.to_string(index=False))

    print("\n=== TABLE 2: Model × Task ===")
    print(table2.to_string(index=False))

    print("\n=== TABLE 3: Language Results (first 15 rows) ===")
    print(table3.head(15).to_string(index=False))

    print("\n=== TABLE 4: Pairwise Win Rates ===")
    # print(table4.to_string(index=False))

    print("\nSaved:")
    print(f"- {OUTPUT_SCORED_CSV}")
    if USE_LLM_FOR_PAIRWISE:
        print(f"- {OUTPUT_PAIRWISE_CSV}")
    print(f"- {OUTPUT_TABLE1_MAIN_RESULTS_CSV}")
    print(f"- {OUTPUT_TABLE2_MODEL_TASK_CSV}")
    print(f"- {OUTPUT_TABLE3_LANGUAGE_CSV}")
    print(f"- {OUTPUT_TABLE4_WINRATE_CSV}")


if __name__ == "__main__":
    main()
