#!/usr/bin/env python3
import base64, hashlib, json, os, sys, time, urllib.parse, urllib.request, urllib.error
from pathlib import Path

CONFIG = Path(__file__).with_name('config.json')

def req(url, method='GET', data=None, headers=None):
    h={'apikey':CFG['key'],'Authorization':'Bearer '+CFG['key'],'x-sync-code':CFG['code']}
    if headers: h.update(headers)
    body=None
    if data is not None:
        body=json.dumps(data).encode(); h['Content-Type']='application/json'
    r=urllib.request.Request(url, data=body, method=method, headers=h)
    with urllib.request.urlopen(r, timeout=30) as x: return x.read()

def get(kind):
    q=urllib.parse.quote(CFG['code'],safe='')
    url=CFG['url'].rstrip('/')+'/rest/v1/shyama_sync_records?sync_code=eq.'+q+'&kind=eq.'+urllib.parse.quote(kind,safe='')+'&select=*'
    return json.loads(req(url))

def pull_media(storage_path, target):
    url=CFG['url'].rstrip('/')+'/storage/v1/object/shyama-media/'+storage_path
    try: data=req(url)
    except Exception as e: print(' media:',e); return False
    target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(data); return True

def safe(v):
    return ''.join(c if c.isalnum() or c in ' ._-()' else '_' for c in str(v or 'file'))[:150]

def sync_once():
    root=Path(CFG['data_dir']).expanduser().resolve(); db=root/'Database'; tasks=root/'Tasks'; db.mkdir(parents=True,exist_ok=True); tasks.mkdir(parents=True,exist_ok=True)
    for kind, fn in [('task_log','task_log.json'),('alarm','alarms.json'),('task_override','task_overrides.json')]:
        rows=get(kind); (db/fn).write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding='utf-8')
    proofs=get('proof')
    (db/'proofs_manifest.json').write_text(json.dumps(proofs,indent=2,ensure_ascii=False),encoding='utf-8')
    for row in proofs:
        if row.get('deleted'): continue
        p=row.get('payload',{}); path=p.get('storage_path');
        if not path: continue
        folder=tasks/safe((p.get('task_name') or p.get('name') or 'Task'))
        ext=Path(p.get('name') or 'file').suffix or ('.pdf' if p.get('type')=='pdf' else '.jpg')
        target=folder/(safe(p.get('name') or p.get('id'))+ext if not safe(p.get('name') or p.get('id')).lower().endswith(ext.lower()) else safe(p.get('name') or p.get('id')))
        # avoid needless download when local file timestamp exists
        if not target.exists(): pull_media(path,target)
    (root/'last_sync.json').write_text(json.dumps({'synced_at':time.strftime('%Y-%m-%dT%H:%M:%S%z'),'status':'ok'},indent=2),encoding='utf-8')
    print(time.strftime('%Y-%m-%d %H:%M:%S'), 'SHYAMA SSD mirror updated')

if not CONFIG.exists():
    print('Missing config.json. Run install_laptop_sync.sh first.'); sys.exit(2)
CFG=json.loads(CONFIG.read_text())
while True:
    try: sync_once()
    except Exception as e: print('Sync error:',e)
    time.sleep(int(CFG.get('interval_seconds',60)))
