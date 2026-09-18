# SHYAMA Routine Quest

## Current Version
**V21 — GitHub Pages + Supabase Sync + Automatic SSD Mirror**

### Current system

- GitHub Pages hosted PWA
- Dark / Light themes
- Daily routine and task tracking
- XP, streaks, statistics and history
- Study PDF proof system
- Workout photo proof system
- Media organized by task
- Supabase cloud synchronization
- Automatic laptop → SSD mirror
- PWA installation on phone and laptop
- Locked proof-required tasks can be safely unticked if accidentally completed

### Sync architecture

Phone / Laptop PWA
→ Supabase
→ Laptop automatic sync service
→ `JARVIS_SSD/SHYAMA_DATA`

### SSD structure

```text
SHYAMA_DATA/
├── Database/
│   ├── alarms.json
│   ├── proofs_manifest.json
│   ├── task_log.json
│   └── task_overrides.json
├── Tasks/
└── last_sync.json
