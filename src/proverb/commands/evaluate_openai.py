from proverb.engine.args import _parse_args
import os
import asyncio
from openai import AsyncOpenAI
from proverb.data.loader import load_raw_dataset

# API_KEY = os.getenv("OPENROUTER_API_KEY")  # 或 OPENROUTER_API_KEY
API_KEY = os.getenv("DEEPSEEK_API_KEY")  # 或 OPENROUTER_API_KEY


async def main():
    model_args, training_args, data_args, task_args = _parse_args()

    model = model_args.model_name_or_path  # 或 openrouter/free
    loaded_datasets = load_raw_dataset(data_args, training_args, task_args)
    sem = asyncio.Semaphore(8)  # 最多 10 个并发请求

    for item in loaded_datasets:
        if task_args.my_debug:
            item["dataset"] = item["dataset"].shuffle(seed=42).select(range(10))

        async with AsyncOpenAI(
            api_key=API_KEY, base_url="https://api.deepseek.com"
        ) as client:
            # 构建要并发调用的 prompt 列表
            prompts = [
                item["dataset"][i]["prompt"] for i in range(len(item["dataset"]))
            ]
            labels = [item["dataset"][i]["label"] for i in range(len(item["dataset"]))]

            # 为每个 prompt 创建一个协程任务
            tasks = [fetch_response(client, p, model, sem) for p in prompts]
            # 并发执行所有任务，并等待返回
            results = await asyncio.gather(*tasks)

            # 打印结果
            for i, text in enumerate(results):
                print(f"Prompt {i}: {text}\n")


async def fetch_response(
    client: AsyncOpenAI, prompt: str, model: str, sem: asyncio.Semaphore, rate_delay=0.2
) -> str:
    # 发起异步请求
    async with sem:
        # 等待以控制速率
        await asyncio.sleep(rate_delay)
        response = await client.chat.completions.create(
            model=model, messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content


if __name__ == "__main__":
    asyncio.run(main())
