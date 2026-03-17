import os

import polars as pl
import typer


MAX_RETRIES = 5

LANGUAGE_LOCTION_PAIRS = {
    "Kenya": [
        "digo",
        "ekegusii",
        "gikuyu",
        "kamba",
        "luo",
        "maasai",
        "meru",
        "nandi",
        "nubian_2",
        "nubian",
        "nyala",
        "olusamia",
        "orma",
        "rendille",
        "samburu",
        "teso",
        "tugen",
        "turkana",
    ],
    "Tanzania": [
        "gweno",
        "kihangaza",
        "kihara",
        "makonde",
        "nyaturu",
        "pare",
        "sukuma",
        "zigula",
    ],
    "DRC": [
        "kwele",
        "tetela",
        "bangubangu",
        "hema",
        "hemba",
        "holoholo",
        "nande",
        "taabwa",
        "tshiluba",
    ],
    "Uganda": ["alur", "chiga", "ganda", "rufumbira", "runyoro", "soga", "tooro"],
    "Somali": ["somali"],
    "Ethiopia": ["borana", "burji"],
}

TASKS = [
    "gen_swa_literal",
    "gen_swa_fig",
    "gen_eng_literal",
    "gen_eng_fig",
]


def _load_all_origin_datasets(root_dir="dataset/African-Proverbs/Data"):
    all_datasets = {}

    for loc, langs in LANGUAGE_LOCTION_PAIRS.items():
        for lang in langs:
            file_path = os.path.join(
                root_dir,
                loc,
                f"{lang}_prov.csv",
            )

            file = pl.read_csv(file_path).rename(lambda c: c.strip())
            all_datasets[(loc, lang)] = file

    return all_datasets


def _load_all_results(
    result_root="results", model_prefix="", result_prefix="generated_predictions"
):
    all_results = {}
    for task_type in TASKS:
        for loc, langs in LANGUAGE_LOCTION_PAIRS.items():
            for lang in langs:
                file_path = os.path.join(
                    result_root,
                    f"{model_prefix}-{task_type}-{loc}".replace("_", "-"),
                    f"generated_predictions_{loc}_{lang}.jsonl",
                )
                try:
                    result = pl.read_ndjson(file_path)
                    all_results[(loc, lang, task_type)] = result
                except FileNotFoundError:
                    print(f"File not found: {file_path}")
                    all_results[(loc, lang, task_type)] = None

    return all_results


def align_columns(dfs: list[pl.DataFrame]) -> list[pl.DataFrame]:
    if not dfs:
        return dfs

    ref_cols = dfs[0].columns

    aligned = []
    for df in dfs:
        aligned.append(df.select(ref_cols))

    return aligned


def check_column_alignment(dfs: list[pl.DataFrame]):
    if len(dfs) < 2:
        print("Need at least two DataFrames")
        return

    ref_cols = dfs[0].columns

    for idx, df in enumerate(dfs[1:], start=1):
        cols = df.columns
        min_len = min(len(ref_cols), len(cols))

        mismatch_found = False

        for i in range(min_len):
            if ref_cols[i] != cols[i]:
                print(f"DF {idx} mismatch starting at column {i}")
                print(f"reference: {ref_cols[i]}")
                print(f"df[{idx}]:  {cols[i]}")
                mismatch_found = True
                break

        if not mismatch_found:
            if len(ref_cols) != len(cols):
                print(f"DF {idx} column count mismatch")
                print(f"reference length: {len(ref_cols)}")
                print(f"df[{idx}] length: {len(cols)}")
            else:
                print(f"DF {idx} columns aligned")


def get_reference_column_name(task_type: str) -> str:
    if task_type == "gen_eng_fig":
        return "eng_figurative"
    elif task_type == "gen_swa_fig":
        return "swa_figurative"
    elif task_type == "gen_eng_literal":
        return "eng_literal"
    elif task_type == "gen_swa_literal":
        return "swa_literal"
    else:
        raise ValueError(f"Unknown task type: {task_type}")


def main(
    result_root: str = "outputs/smollm3-3b",
    data_root: str = "/home/2533494W/project/proverb/dataset/African-Proverbs/Data",
    model_prefix: str = "smollm3-3b-it",
    output_path: str = "outputs/all_results",
):
    all_datasets = _load_all_origin_datasets()
    all_results = _load_all_results(result_root=result_root, model_prefix=model_prefix)

    all_processed_results = {}
    for key, result in all_results.items():
        if result is None:
            print(f"Missing result for {key}")
            continue
        loc, lang, task_type = key
        dataset = all_datasets.get((loc, lang))
        if dataset is None:
            print(f"Missing dataset for {loc}, {lang}")
            continue

        all_processed_results[key] = (
            pl.concat([dataset, result], how="horizontal")
            .with_columns(
                pl.lit(task_type).alias("task"),
                pl.lit(loc).alias("location"),
                pl.lit(lang).alias("language"),
                pl.lit(model_prefix).alias("model"),
                pl.col(get_reference_column_name(task_type)).alias("reference"),
            )
            .rename(
                {
                    f"{lang}_prov": "source_proverb",
                    "predict": "prediction",
                }
            )
        )

    all_processed_results = list(all_processed_results.values())
    aligned_results = align_columns(all_processed_results)
    check_column_alignment(all_processed_results)

    re = pl.concat(aligned_results, how="vertical").drop("prompt")
    re = re.with_row_index("proverb_id")
    re.write_csv(os.path.join(output_path, f"{model_prefix}_all_results.csv"))


if __name__ == "__main__":
    typer.run(main)
