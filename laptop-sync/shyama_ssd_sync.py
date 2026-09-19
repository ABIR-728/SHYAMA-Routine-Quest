#!/usr/bin/env python3
"""SHYAMA cloud -> SSD mirror with an append-only local archive.

The live Database/*.json files are the current mirror.  Archive/ is never
pruned by this script: each new cloud record version is appended to a JSONL
history file, and a daily point-in-time snapshot is kept on the SSD.
"""
import hashlib, json, os, sys, time, urllib.parse, urllib.request
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

def record_key(row):
    # updated_at makes edits append a new immutable version instead of replacing history.
    raw='|'.join(str(row.get(k,'')) for k in ('kind','record_id','updated_at','deleted'))
    return hashlib.sha256(raw.encode()).hexdigest()

def archive_records(root, rows_by_kind):
    archive=root/'Archive'; records=archive/'Records'; records.mkdir(parents=True,exist_ok=True)
    index_path=archive/'archive_index.json'
    try: seen=set(json.loads(index_path.read_text(encoding='utf-8')).get('keys',[])) if index_path.exists() else set()
    except Exception: seen=set()
    added=0
    for kind, rows in rows_by_kind.items():
        out=records/(safe(kind)+'.jsonl')
        with out.open('a',encoding='utf-8') as f:
            for row in rows:
                key=record_key(row)
                if key in seen: continue
                f.write(json.dumps(row,ensure_ascii=False,separators=(',',':'))+'\n')
                seen.add(key); added+=1
    index_path.write_text(json.dumps({'version':1,'keys':sorted(seen)},indent=2),encoding='utf-8')
    return added

def daily_snapshot(root, db):
    """Create one immutable database snapshot per calendar day."""
    snap_root=root/'Archive'/'Snapshots'; day=time.strftime('%Y-%m-%d'); folder=snap_root/day
    marker=folder/'.complete'
    if marker.exists(): return False
    folder.mkdir(parents=True,exist_ok=True)
    for src in sorted(db.glob('*.json')):
        (folder/src.name).write_bytes(src.read_bytes())
    marker.write_text(time.strftime('%Y-%m-%dT%H:%M:%S%z')+'\n',encoding='utf-8')
    return True

def sync_once():
    root=Path(CFG['data_dir']).expanduser().resolve(); db=root/'Database'; tasks=root/'Tasks'
    db.mkdir(parents=True,exist_ok=True); tasks.mkdir(parents=True,exist_ok=True)
    rows_by_kind={}
    for kind, fn in [('task_log','task_log.json'),('alarm','alarms.json'),('task_override','task_overrides.json'),('challenge_state','challenge_state.json')]:
        rows=get(kind); rows_by_kind[kind]=rows
        (db/fn).write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding='utf-8')
    proofs=get('proof'); rows_by_kind['proof']=proofs
    (db/'proofs_manifest.json').write_text(json.dumps(proofs,indent=2,ensure_ascii=False),encoding='utf-8')

    # Keep proof files locally even if a cloud row is later marked deleted.
    # Never remove anything from Tasks/ during sync.
    for row in proofs:
        if row.get('deleted'): continue
        p=row.get('payload',{}); path=p.get('storage_path')
        if not path: continue
        folder=tasks/safe((p.get('task_name') or p.get('name') or 'Task'))
        name=safe(p.get('name') or p.get('id'))
        ext=Path(p.get('name') or 'file').suffix or ('.pdf' if p.get('type')=='pdf' else '.jpg')
        target=folder/(name if name.lower().endswith(ext.lower()) else name+ext)
        if not target.exists(): pull_media(path,target)

    added=archive_records(root,rows_by_kind)
    snap=daily_snapshot(root,db)
    (root/'last_sync.json').write_text(json.dumps({
        'synced_at':time.strftime('%Y-%m-%dT%H:%M:%S%z'),'status':'ok',
        'archived_new_versions':added,'daily_snapshot_created':snap,
        'storage_policy':'append-only local archive; sync never deletes Tasks or Archive'
    },indent=2),encoding='utf-8')
    print(time.strftime('%Y-%m-%d %H:%M:%S'), 'SHYAMA SSD mirror updated; archived',added,'new record version(s)')

if not CONFIG.exists():
    print('Missing config.json. Run install_laptop_sync.sh first.'); sys.exit(2)
CFG=json.loads(CONFIG.read_text())
while True:
    try: sync_once()
    except Exception as e: print('Sync error:',e)
    time.sleep(int(CFG.get('interval_seconds',60)))
