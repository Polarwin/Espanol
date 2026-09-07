"""Offline, sentence-level Spanish BARTO correction experiment."""
import argparse
import json
import statistics
import time
from pathlib import Path
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--model-home', required=True, type=Path)
parser.add_argument('--text', help='One Spanish sentence, without an instruction prefix.')
parser.add_argument('--output', type=Path)
parser.add_argument('--runs', type=int, default=2)
parser.add_argument('--threads', type=int, default=4)
args = parser.parse_args()
if args.threads < 1 or args.runs < 1:
    parser.error('threads and runs must be positive')
torch.set_num_threads(args.threads)
started = time.perf_counter()
tokenizer = AutoTokenizer.from_pretrained(args.model_home/'model', local_files_only=True)
model = AutoModelForSeq2SeqLM.from_pretrained(args.model_home/'model', local_files_only=True).eval()
report = {'manifest': json.loads((args.model_home/'manifest.json').read_text()),
          'load_seconds': round(time.perf_counter()-started, 3),
          'parameters': sum(p.numel() for p in model.parameters()),
          'device': 'cpu', 'threads': args.threads,
          'generation_config': model.generation_config.to_dict(), 'results': []}
cases = [{'id':'custom','kind':'custom','text':args.text}] if args.text is not None else json.loads(Path(__file__).with_name('cases.json').read_text())
print(f"Loaded {report['parameters']:,} parameters on CPU in {report['load_seconds']}s", flush=True)
for run in range(args.runs):
    for case in cases:
        token_count = len(tokenizer(case['text'])['input_ids'])
        if token_count > 128:
            parser.error('Input exceeds 128 tokens; use shorter individual sentences.')
        started = time.perf_counter()
        inputs = tokenizer(case['text'], max_length=128, padding='max_length', return_tensors='pt')
        with torch.inference_mode():
            output = model.generate(**inputs, max_new_tokens=128, do_sample=False)
        text = tokenizer.decode(output[0], skip_special_tokens=True)
        row = {**case, 'run':run+1, 'output':text,
               'seconds':round(time.perf_counter()-started, 3),
               'changed':text != case['text'],
               'ended_with_eos':int(output[0][-1]) == model.config.eos_token_id}
        if 'expected' in case:
            row['exact_reference_match'] = text == case['expected']
        report['results'].append(row)
        print(json.dumps(row, ensure_ascii=False), flush=True)
report['warm_median_seconds'] = statistics.median(r['seconds'] for r in report['results'][1:] or report['results'])
if args.output:
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
print(f"Warm median: {report['warm_median_seconds']:.3f}s")
