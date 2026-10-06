#!/usr/bin/env python3
"""Install/update only our 06:00 daily cron entry, preserving existing jobs."""
from datetime import datetime
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[1]
timezone = subprocess.check_output(['timedatectl', 'show', '-p', 'Timezone', '--value'], text=True).strip()
if timezone != 'Europe/Madrid':
    raise SystemExit('Expected host timezone Europe/Madrid; no crontab changes made.')
previous = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
if previous.returncode and 'no crontab for' not in previous.stderr.lower():
    raise SystemExit(previous.stderr)
marker = '# vamos-daily-news-reading'
lines = [line for line in previous.stdout.splitlines() if marker not in line]
entry = f'0 6 * * * cd {root} && {root}/bin/python {root}/tools/daily_reading.py >> {root}/logs/daily-reading.log 2>&1 {marker}'
lines.append(entry)
(root / 'backups').mkdir(exist_ok=True)
(root / 'logs').mkdir(exist_ok=True)
backup = root / 'backups' / ('crontab-before-daily-reading-' + datetime.now().strftime('%Y%m%d-%H%M%S') + '.txt')
backup.write_text(previous.stdout, encoding='utf-8')
subprocess.run(['crontab', '-'], input='\n'.join(lines) + '\n', text=True, check=True)
installed = subprocess.check_output(['crontab', '-l'], text=True)
assert entry in installed
print('Installed: daily at 06:00 Europe/Madrid (including daylight-saving changes).')
print(f'Previous crontab saved to {backup}')
print(entry)
