import numpy

from transformers import AutoTokenizer


tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.2-1B-Instruct")


messages = [
    {"role": "user", "content": "What is the capital of Germany?"},
]

print(tokenizer.apply_chat_template(messages, tokenize=False))
print(tokenizer.eos_token)
