import sys

sys.path.append("./src")

from openai import OpenAI
from proverb.engine.args import DataArguments, TaskArguments
from proverb.data.loader import load_raw_dataset
from transformers.training_args import TrainingArguments
import os

data_args = DataArguments(
    dataset_dir="dataset/African-Proverbs/Data",
    template_name="mistral",
    location="DRC",
    language="bangubangu",
    override_cache=False,
    processing_num_workers=4,
    few_shot_num=0,
)

task_args = TaskArguments(
    task_type="gen_swa_literal",
)
training_args = TrainingArguments(output_dir="./tmp")

# API_KEY = os.getenv("OPENROUTER_API_KEY")
#
# # 创建 OpenAI 客户端但改 base_url
# client = OpenAI(api_key=API_KEY, base_url="https://openrouter.ai/api/v1")
#
# # 发起聊天请求
# resp = client.chat.completions.create(
#     model="openrouter/free",
#     messages=[
#         {"role": "system", "content": "You are a helpful assistant."},
#         {"role": "user", "content": "用中文解释 OpenRouter 支持 openai 库 吗？"},
#     ],
# )
#
# print(resp.choices[0].message.content)


loaded_datasets = load_raw_dataset(data_args, training_args, task_args)


for item in loaded_datasets:
    print("INPUT:\n")
    print(item["dataset"][0]["proverb"])

import os
import asyncio
from openai import AsyncOpenAI

API_KEY = os.getenv("OPENROUTER_API_KEY")  # 或 OPENROUTER_API_KEY
MODEL = "openrouter/free"  # 或 openrouter/free


async def fetch_response(client: AsyncOpenAI, prompt: str) -> str:
    # 发起异步请求
    response = await client.chat.completions.create(
        model=MODEL, messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


async def main():
    # 创建异步客户端实例
    async with AsyncOpenAI(api_key=API_KEY) as client:
        # 构建要并发调用的 prompt 列表
        prompts = [f"写一句关于数字 {i} 的有趣诗句" for i in range(10)]

        # 为每个 prompt 创建一个协程任务
        tasks = [fetch_response(client, p) for p in prompts]

        # 并发执行所有任务，并等待返回
        results = await asyncio.gather(*tasks)

        # 打印结果
        for i, text in enumerate(results):
            print(f"Prompt {i}: {text}\n")


if __name__ == "__main__":
    asyncio.run(main())
