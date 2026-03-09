from typing import Optional
from proverb.engine.args import DataArguments
import os
import importlib.util
import sys

# GENERATE_PROMPT_LITERAL = (
#     "I will provide you with a proverb in {source_language}. \n"
#     "Please give its figurative meaning in {target_language}. \n"
#     "Respond only with the meaning, without any additional explanations. \n"
#     "Proverb: {proverb}"
# )


def _import_variable_from_file(file_path, variable_name):
    # 生成模块名
    module_name = f"module_{hash(file_path)}"

    # 创建模块规范
    spec = importlib.util.spec_from_file_location(module_name, file_path)

    if spec is None:
        raise ImportError(f"无法从 {file_path} 创建模块规范")

    # 创建模块
    module = importlib.util.module_from_spec(spec)

    # 将模块添加到 sys.modules
    sys.modules[module_name] = module

    # 执行模块
    spec.loader.exec_module(module)

    # 获取变量
    if hasattr(module, variable_name):
        return getattr(module, variable_name)
    else:
        raise AttributeError(f"模块中没有名为 '{variable_name}' 的变量")


GENERATE_PROMPT_LITERAL = (
    "**Task:**\nYou are a professional translator specializing in proverbs \n"
    "Your task is to translate the following proverb from {source_language} to {target_language} literally. \n\n"
    "A literal translation MUST: \n"
    "Preserve the imagery and entities (animals, objects, actions).\n"
    "Avoid interpretation, explanation, or moralization.\n"
    "Sound odd or ambiguous on purpose.\n"
    "Be word- or phrase-aligned as much as possible.\n"
    "you should NOT:\n"
    "Replace the proverb with an equivalent proverb.\n"
    "Explain the lesson.\n"
    "Use abstract language.\n"
    "You should respond only with the literal translation, without any additional explanations. \n"
    "here is an example of the expected format:\n\n"
    "**Input**:\n"
    "A proverb in {source_language}\n\n"
    "**Output**:\n"
    "The literal translation of the proverb in {target_language}.\n\n"
    "Now, please translate the following proverb:\n\n"
    "**Input**:\n{proverb}\n\n"
    "**Output**:\n"
)
GENERATE_PROMPT_FIGURATIVE = (
    "**Task:**\nYou are a professional translator specializing in proverbs \n"
    "Your task is to infer the figurative meaning of the following proverb from {source_language} to {target_language}. \n\n"
    "A figurative translation MUST:\n"
    "Explicitly state the underlying principle.\n"
    "Remove metaphor, imagery, and animals.\n"
    "Use plain, abstract language.\n"
    "Be culturally faithful, not proverb-matching.\n\n"
    "Do NOT:\n"
    "Use another proverb.\n"
    "Retain imagery.\n"
    "Be poetic or idiomatic.\n"
    "You should respond only with the figurative translation, without any additional explanations. \n"
    "here is an example of the expected format:\n\n"
    "**Input**:\n"
    "A proverb in {source_language}\n\n"
    "**Output**:\n"
    "The figurative meaning of the proverb in {target_language}.\n\n"
    "Now, please translate the following proverb:\n\n"
    "**Input**:\n{proverb}\n\n"
    "**Output**:\n"
)

# GENERATE_PROMPT_FIGURATIVE = (
#     "I will provide you with a proverb in {source_language}. \n"
#     "Please give its literal meaning in {target_language}. \n"
#     "Respond only with the meaning, without any additional explanations. \n"
#     "Proverb: {proverb}"
# )
#
FEW_SHOTS_GENERATE_PROMPT_LITERAL = (
    "**Task:**\nYou are a professional translator specializing in proverbs \n"
    "Your task is to translate the following proverb from {source_language} to {target_language} literally. \n\n"
    "**Input**:\n"
    "A proverb in {source_language}\n\n"
    "**Output**:\n"
    "The literal translation of the proverb in {target_language}.\n\n"
    "**Examples**:\n\n"
    "{content}"
    "\n**Input**:\n{proverb}\n\n"
    "**Output**:\n"
)


FEW_SHOTS_GENERATE_PROMPT_FIGURATIVE = (
    "**Task:**\nYou are a professional translator specializing in proverbs \n"  # TODO: add native speaker
    "Your task is to infer the figurative meaning of the following proverb from {source_language} to {target_language}. \n\n"
    "**Input**:\n"
    "A proverb in {source_language}\n\n"
    "**Output**:\n"
    "The figurative meaning of the proverb in {target_language}.\n\n"
    "**Examples**:\n\n"
    "{content}"
    "\n**Input**:\n{proverb}\n\n"
    "**Output**:\n"
)


def get_prompt_by_task(
    task_type: str,
    source_language: Optional[str],
    proverb: Optional[str] = None,
) -> str:
    if task_type == "gen_swa_literal":
        return GENERATE_PROMPT_LITERAL.format(
            source_language=source_language,
            target_language="Swahili",
            proverb=proverb,
        )
    elif task_type == "gen_eng_literal":
        return GENERATE_PROMPT_LITERAL.format(
            source_language=source_language,
            target_language="English",
            proverb=proverb,
        )
    elif task_type == "gen_swa_fig":
        return GENERATE_PROMPT_FIGURATIVE.format(
            source_language=source_language,
            target_language="Swahili",
            proverb=proverb,
        )
    elif task_type == "gen_eng_fig":
        return GENERATE_PROMPT_FIGURATIVE.format(
            source_language=source_language,
            target_language="English",
            proverb=proverb,
        )
    else:
        raise ValueError(f"Unknown task type: {task_type}")


def get_few_shots_prompt_by_task(
    task_type: str,
    source_language: Optional[str],
    proverb: Optional[str] = None,
    location: Optional[str] = None,
    data_args: Optional[DataArguments] = None,
):
    if task_type == "gen_swa_literal":
        file_name = "swa_literal.py"
        v_name = "GENERATE_PROMPT_LITERAL"
    elif task_type == "gen_eng_literal":
        file_name = "eng_literal.py"
        v_name = "GENERATE_PROMPT_LITERAL"
    elif task_type == "gen_swa_fig":
        file_name = "swa_figurative.py"
        v_name = "GENERATE_PROMPT_FIGURATIVE"
    elif task_type == "gen_eng_fig":
        file_name = "eng_figurative.py"
        v_name = "GENERATE_PROMPT_FIGURATIVE"
    else:
        raise ValueError(f"Unknown task type: {task_type}")

    python_file_path = os.path.join(
        data_args.dataset_dir,
        "../",
        "few_shot_prompts",
        location,
        source_language,
        file_name,
    )

    return _import_variable_from_file(python_file_path, v_name).format(
        source_language=source_language,
        target_language="swahili" if "swa" in task_type else "english",
        proverb=proverb,
    )
