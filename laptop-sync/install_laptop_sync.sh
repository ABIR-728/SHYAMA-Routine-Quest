#!/usr/bin/env bash
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
read -r -p "Supabase Project URL: " SBURL
read -r -p "Supabase anon public key: " SBKEY
read -r -p "Private Sync Code (same on phone and laptop): " SBCODE
read -r -p "SSD folder for SHYAMA data (example /media/$USER/MySSD/SHYAMA_DATA): " DATADIR
mkdir -p "$DATADIR"
python3 - "$HERE" "$SBURL" "$SBKEY" "$SBCODE" "$DATADIR" <<'PY'
import json,sys
from pathlib import Path
here,url,key,code,data=sys.argv[1:]
Path(here,'config.json').write_text(json.dumps({'url':url,'key':key,'code':code,'data_dir':data,'interval_seconds':60},indent=2))
PY
chmod +x "$HERE/shyama_ssd_sync.py"
mkdir -p "$HOME/.config/systemd/user"
cat > "$HOME/.config/systemd/user/shyama-ssd-sync.service" <<EOF
[Unit]
Description=SHYAMA automatic SSD mirror
After=network-online.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 $HERE/shyama_ssd_sync.py
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
EOF
systemctl --user daemon-reload
systemctl --user enable --now shyama-ssd-sync.service
echo
echo "SHYAMA SSD sync is now running automatically after you log in."
echo "Check: systemctl --user status shyama-ssd-sync"
