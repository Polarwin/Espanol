#!/usr/bin/env python3
"""Opt-in live local-model smoke test. Run with ./bin/python tools/smoke_reading.py.

Creates a uniquely named temporary user, generates one news reading through the
running API, checks saved answers, and removes only its own test rows afterwards.
No existing learner data is used. Needs the API's JWT configuration in the env.
"""
import json
import sys
import time
from pathlib import Path
from uuid import uuid4
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.app.db import SessionLocal
from backend.app.models import ReadingPractice, User
from backend.app.services.security import create_token


def main():
    with SessionLocal() as db:
        user = User(email=f'reading-smoke-{uuid4().hex}@example.invalid', password_hash='disabled',
                    display_name='Reading smoke test', placement_completed=True)
        db.add(user)
        db.commit()
        user_id, token = user.id, create_token(user.id)
    terminal = False
    def request(path='', body=None, method=None):
        req = Request('http://127.0.0.1:8011/api/reading' + path,
                      json.dumps(body).encode() if body is not None else None,
                      {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}, method=method)
        with urlopen(req, timeout=30) as response:
            return json.load(response)
    try:
        job = request(body={'source': 'news', 'level': 'A2'})
        last = None
        for _ in range(480):
            job = request('/' + job['id'])
            status = (job['status'], job['stage'])
            if status != last:
                print(status, flush=True)
                last = status
            if job['status'] in {'ready', 'failed'}:
                terminal = True
                break
            time.sleep(5)
        if job['status'] != 'ready':
            raise RuntimeError(job.get('error') or 'Generation still running')
        pack = job['pack']
        assert len(pack['questions']) == 5 and len(pack['vocabulary']) == 8
        assert pack['translation'] and pack['review_status'] == 'draft'
        result = request('/' + job['id'] + '/answers', {'answers': {'0': 'Respuesta de prueba'}}, 'PUT')
        assert result['answers']['0'] == 'Respuesta de prueba'
        assert request('/' + job['id'])['answers'] == result['answers']
        print('PASS: live news → local model → reading, translation, 5 open questions, 8 bilingual definitions; answers persisted.', flush=True)
    finally:
        if terminal:
            with SessionLocal() as db:
                from sqlalchemy import delete
                db.execute(delete(ReadingPractice).where(ReadingPractice.user_id == user_id))
                db.execute(delete(User).where(User.id == user_id))
                db.commit()
            print('Removed only the temporary smoke-test account and its reading.', flush=True)
        else:
            print(f'Test user {user_id} retained because generation may still be running.', flush=True)


if __name__ == '__main__':
    main()
