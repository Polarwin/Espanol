"""Offline CPU smoke test of the pretrained model, NOT a validated corrector."""
import argparse
import json
import time
from pathlib import Path
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--model-home', required=True, type=Path)
parser.add_argument('--text', help='Exact input to send to the model, including any prefix/mask tokens.')
parser.add_argument('--output', type=Path, help='Save the inputs, outputs and timings as JSON.')
parser.add_argument('--max-new-tokens', type=int, default=64)
parser.add_argument('--threads', type=int, default=4)
args = parser.parse_args()
if args.threads < 1 or not 1 <= args.max_new_tokens <= 512:
    parser.error('threads must be positive; max-new-tokens must be between 1 and 512')
torch.set_num_threads(args.threads)
started = time.perf_counter()
tokenizer = AutoTokenizer.from_pretrained(args.model_home / 'model', local_files_only=True)
model = AutoModelForSeq2SeqLM.from_pretrained(args.model_home / 'model', local_files_only=True).eval()
load_seconds = time.perf_counter() - started
cases = [args.text] if args.text is not None else [
    'Soy <extra_id_0> años.',
    'Tengo veinte años y me <extra_id_0> las películas españolas.',
    'Corrige la gramática: Soy veinte años y me gusta las películas españolas.',
    'Corrige la gramática: Ayer voy al mercado y compro dos manzanas.',
    'Corrige la gramática: Depende de que tengamos tiempo.',
    'Cliente: Quiero un café con leche de soja. Camarera:',
]
report = {'manifest': json.loads((args.model_home / 'manifest.json').read_text()),
          'load_seconds': round(load_seconds, 3), 'device': 'cpu', 'threads': args.threads,
          'decoding': 'greedy', 'max_new_tokens': args.max_new_tokens, 'results': []}
print(f'Loaded on CPU in {load_seconds:.2f}s. This checkpoint is pretrained, not correction-fine-tuned.', flush=True)
for text in cases:
    started = time.perf_counter()
    inputs = tokenizer(text, return_tensors='pt', truncation=True, max_length=512)
    with torch.inference_mode():
        output = model.generate(**inputs, max_new_tokens=args.max_new_tokens, do_sample=False)
    row = {'input': text, 'output': tokenizer.decode(output[0], skip_special_tokens=True),
           'raw_output': tokenizer.decode(output[0], skip_special_tokens=False),
           'seconds': round(time.perf_counter()-started, 3),
           'generated_tokens': len(output[0])-1,
           'ended_with_eos': int(output[0][-1]) == model.config.eos_token_id}
    report['results'].append(row)
    print(json.dumps(row, ensure_ascii=False), flush=True)
if args.output:
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
