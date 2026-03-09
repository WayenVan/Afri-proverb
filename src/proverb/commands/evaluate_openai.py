from proverb.engine.args import _parse_args
import os
import asyncio
from openai import AsyncOpenAI
from proverb.data.loader import load_raw_dataset
from typing import List
from evaluate import load
import json
from sacrebleu import corpus_bleu
from tqdm.asyncio import tqdm_asyncio
import logging

logging.getLogger("httpx").setLevel(logging.WARNING)

# API_KEY = os.getenv("OPENROUTER_API_KEY")  # 或 OPENROUTER_API_KEY
charf = load("chrf")
comet = load("comet")


async def main():
    model_args, training_args, data_args, task_args = _parse_args()

    os.makedirs(training_args.output_dir, exist_ok=True)

    model = model_args.model_name_or_path  # 或 openrouter/free
    loaded_datasets = load_raw_dataset(data_args, training_args, task_args)
    sem = asyncio.Semaphore(task_args.api_semophore)  # 最多 10 个并发请求
    API_KEY = os.getenv(task_args.api_key_env_name)  # 或 OPENROUTER_API_KEY

    metrics_results = []
    for item in loaded_datasets:
        if task_args.my_debug:
            item["dataset"] = item["dataset"].shuffle(seed=42).select(range(10))

        async with AsyncOpenAI(api_key=API_KEY, base_url=task_args.api_url) as client:
            # 构建要并发调用的 prompt 列表
            prompts = [
                item["dataset"][i]["prompt"] for i in range(len(item["dataset"]))
            ]
            sources = [
                item["dataset"][i]["source"] for i in range(len(item["dataset"]))
            ]
            labels = [item["dataset"][i]["label"] for i in range(len(item["dataset"]))]

            # 为每个 prompt 创建一个协程任务
            tasks = [
                fetch_response(client, p, model, sem, rate_delay=task_args.api_delay)
                for p in prompts
            ]
            # 并发执行所有任务，并等待返回
            results = await tqdm_asyncio.gather(
                *tasks, desc=f"Processing {item['location']} - {item['language']}"
            )

            m = metrics(results, sources, labels)
            metrics_results.append(
                {
                    "task_type": task_args.task_type,
                    "location": item["location"],
                    "language": item["language"],
                    "results": m,
                }
            )

            save_predictions(
                predictions=results,
                prompts=prompts,
                labels=labels,
                training_args=training_args,
                file_name=f"generated_predictions_{item['location']}_{item['language']}.jsonl",
            )

    with open(
        os.path.join(training_args.output_dir, "evaluation_results.json"), "w"
    ) as f:
        json.dump(metrics_results, f, indent=4)


async def fetch_response(
    client: AsyncOpenAI, prompt: str, model: str, sem: asyncio.Semaphore, rate_delay=0.2
) -> str:
    # 发起异步请求
    async with sem:
        # 等待以控制速率
        await asyncio.sleep(rate_delay)
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=1024,
            reasoning_effort="none",
        )
        content = response.choices[0].message.content
        if content is None:
            print(f"Warning: Received empty response for prompt: {prompt}")
            print(f"Full response: {response}")
            content = ""
        return content.strip()


def metrics(predicts: List[str], sources: List[str], labels: list[str]):
    bleu_score = corpus_bleu(predicts, [[label] for label in labels])
    charf_score = charf.compute(
        predictions=predicts,
        references=labels,
    )
    chrf_pp_score = charf.compute(
        predictions=predicts,
        references=labels,
        char_order=6,
        word_order=2,
    )
    ret = {
        "bleu": round(bleu_score.score, 6),
        "chrf": round(charf_score["score"], 6),
        "chrf++": round(chrf_pp_score["score"], 6),
    }

    comet_score = comet.compute(
        predictions=predicts,
        references=labels,
        sources=sources,
    )

    ret["comet"] = round(comet_score["mean_score"], 6)
    return ret


def save_predictions(
    predictions: List[str],
    prompts: List[str],
    labels: List[str],
    training_args,
    file_name: str = "generated_predictions.jsonl",
):
    output_prediction_file = os.path.join(training_args.output_dir, file_name)

    with open(output_prediction_file, "w", encoding="utf-8") as f:
        for text, pred, label in zip(prompts, predictions, labels):
            f.write(
                json.dumps(
                    {"prompt": text, "predict": pred, "label": label},
                    ensure_ascii=False,
                )
                + "\n"
            )


if __name__ == "__main__":
    asyncio.run(main())
