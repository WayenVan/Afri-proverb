export PYTHONPATH="./src:$PYTHONPATH"
python -m proverb.commands.assemble_results \
  --result-root outputs/smollm3-3b \
  --data-root dataset/African-Proverbs/Data \
  --output-path outputs/all_results \
  --model-prefix smollm3-3b-it
