# SHYAMA V19 — Automatic Phone ↔ Cloud ↔ Laptop/SSD

This version keeps the app local-first and adds an automatic cloud bridge. When configured with the same Supabase URL, anon key and private Sync Code on phone and laptop, task completion, alarms, task edits and proof media are synced. The included laptop companion mirrors the cloud data into a folder on your laptop or connected SSD every 60 seconds while Ubuntu is running.

## One-time setup
1. Create a Supabase project.
2. Open its SQL Editor and run `supabase-schema.sql`.
3. On each SHYAMA install open Settings → Cross-Device Sync and enter the same Project URL, anon key and private Sync Code.
4. On Ubuntu, put `laptop-sync` somewhere convenient, then run `./install_laptop_sync.sh` and enter the same credentials plus the SSD destination, e.g. `/media/$USER/MySSD/SHYAMA_DATA`.
5. The Ubuntu user service starts automatically after login and mirrors data every 60 seconds.

The SSD mirror is an archive. The SHYAMA app remains the working interface; the laptop app itself also syncs with the cloud when opened.

Do not put PDFs, workout photos or sync codes into a public GitHub repository. GitHub can host the app code, but personal data should stay in Supabase/your SSD.


This V20 build is preconfigured for the SHYAMA Routine Quest Supabase project. You only need to choose one private Sync Code and use the same code on your phone and laptop.
