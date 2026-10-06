#!/usr/bin/env python3
"""Replace only the old daily reading cron with the folder-watcher service."""
from datetime import datetime
from pathlib import Path
import shutil
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
subprocess.run([sys.executable, str(root / 'tools/watch_news_readings.py'), '--initialize'], cwd=root, check=True)
previous = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
if previous.returncode and 'no crontab for' not in previous.stderr.lower():
    raise SystemExit(previous.stderr)
lines = [line for line in previous.stdout.splitlines() if '# vamos-daily-news-reading' not in line]
backup = root / 'backups' / ('crontab-before-news-watcher-' + datetime.now().strftime('%Y%m%d-%H%M%S') + '.txt')
backup.write_text(previous.stdout, encoding='utf-8')
subprocess.run(['crontab', '-'], input='\n'.join(lines) + '\n', text=True, check=True)
unit = 'vamos-news-reading-watcher.service'
destination = Path.home() / '.config/systemd/user' / unit
destination.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(root / 'deploy/systemd' / unit, destination)
subprocess.run(['systemctl', '--user', 'daemon-reload'], check=True)
subprocess.run(['systemctl', '--user', 'enable', '--now', unit], check=True)
subprocess.run(['systemctl', '--user', 'is-active', unit], check=True)
print('Daily reading cron removed; new-video watcher enabled. Other cron jobs preserved.')
print('Generated files: /srv/files/static/SpanishReading/news-<video-id>-<a1|a2|b1|b2>/')
print(f'Crontab backup: {backup}')
