# SHYAMA Routine Quest

## Current Version
**V30 — GitHub Pages + Supabase Sync + Automatic SSD Mirror + Today Add Task**

SHYAMA Routine Quest is a local-first Progressive Web App (PWA) for managing daily study, tuition, fitness, government-job preparation, GATE/CSIR-NET preparation, XP, proof-based tasks and personal routine progress.

## V30 features

- GitHub Pages hosted PWA
- Dark / Light themes
- All app pages use the same dark visual style in Dark mode
- Daily routine and task tracking
- **Add Task directly from the Today page**
- Added tasks can include:
  - Task name
  - Start time
  - End time
  - Category
  - XP
- Added tasks can be edited or deleted
- Added tasks are included in Today progress, XP and statistics
- Study PDF proof requirements
- Workout photo proof requirement
- Proof-required categories:
  - 4th Sem → PDF
  - GATE/NET → PDF
  - Govt Job → PDF
  - Fitness → workout photo
- Proof-required tasks can be safely unticked if accidentally completed
- Media organized by task
- Motivation/inspiration image collection
- XP, streaks, statistics and history
- Focus timer
- Alarms/notifications
- Weekly Monday–Sunday routine
- Settings appearance switch for Dark / Light mode
- Supabase cloud synchronization
- Automatic laptop → SSD mirror
- PWA installation on phone and laptop
- GitHub Pages permanent HTTPS hosting

## Sync architecture

Phone / Laptop PWA
→ Supabase
→ Laptop automatic sync service
→ `JARVIS_SSD/SHYAMA_DATA`

## SSD structure

```text
SHYAMA_DATA/
├── Database/
│   ├── alarms.json
│   ├── proofs_manifest.json
│   ├── task_log.json
│   └── task_overrides.json
├── Tasks/
│   └── <task name>/
└── last_sync.json
