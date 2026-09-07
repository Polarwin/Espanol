"""Bounded, loopback-only correction worker; no app database or cloud access."""
import json
import os
import threading
import time
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from backend.app.services.ai.text_safety import acceptable_edit

os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'
import pysbd
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

root = Path(os.environ.get('VAMOS_BARTO_HOME', Path(__file__).resolve().parents[2] / '.local-models/spanish-barto'))
torch.set_num_threads(3)
tokenizer = AutoTokenizer.from_pretrained(root / 'model', local_files_only=True)
model = AutoModelForSeq2SeqLM.from_pretrained(root / 'model', local_files_only=True).eval()
segmenter = pysbd.Segmenter(language='es', clean=False, char_span=True)
lock = threading.Lock()


def correct_text(text):
    spans = segmenter.segment(text)
    edits = []
    processed = 0
    started = time.monotonic()
    for span in spans[:12]:
        sentence = span.sent.strip()
        if not sentence or len(tokenizer(sentence)['input_ids']) > 128 or time.monotonic()-started > 8:
            continue
        inputs = tokenizer(sentence, max_length=128, padding='max_length', return_tensors='pt')
        with torch.inference_mode():
            output = model.generate(**inputs, max_new_tokens=128, do_sample=False)
        if len(output[0]) >= 129:
            continue
        suggested = tokenizer.decode(output[0], skip_special_tokens=True).strip()
        if not suggested or not acceptable_edit(sentence, suggested):
            continue
        processed += 1
        offset = span.start + len(span.sent) - len(span.sent.lstrip())
        edits.append((offset, offset + len(sentence), suggested))
    suggested = text
    for start, end, replacement in reversed(edits):
        suggested = suggested[:start] + replacement + suggested[end:]
    skipped = len(spans) - processed
    status = 'partial' if skipped else ('suggestions' if suggested != text else 'no_suggestion')
    return dict(status=status, original=text, suggested=suggested, processed=processed, skipped=skipped)


class Handler(BaseHTTPRequestHandler):
    def setup(self):
        super().setup()
        self.connection.settimeout(15)

    def send(self, status, body):
        encoded = json.dumps(body, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(encoded)))
        self.end_headers()
        try:
            self.wfile.write(encoded)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def do_GET(self):
        self.send(200, {'status': 'ok', **json.loads((root/'manifest.json').read_text())}) if self.path == '/health' else self.send(404, {'error':'not found'})

    def do_POST(self):
        if self.path != '/correct':
            return self.send(404, {'error':'not found'})
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 16000:
                return self.send(413, {'error':'request too large'})
            body = json.loads(self.rfile.read(length))
            text = body.get('text')
            if not isinstance(text, str) or not text.strip() or len(text) > 2000:
                return self.send(422, {'error':'send 1–2000 characters'})
        except (ValueError, AttributeError):
            return self.send(400, {'error':'invalid JSON'})
        if not lock.acquire(blocking=False):
            return self.send(429, {'error':'busy'})
        try:
            self.send(200, correct_text(text))
        except Exception:
            self.send(503, {'error':'correction unavailable'})
        finally:
            lock.release()

    def log_message(self, *args):
        pass


if __name__ == '__main__':
    ThreadingHTTPServer(('127.0.0.1', 8351), Handler).serve_forever()
