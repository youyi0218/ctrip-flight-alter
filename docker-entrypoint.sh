#!/bin/sh
set -eu

APP_DIR="${APP_DIR:-/app}"
SEED_DIR="/opt/qunar-flight-alter-seed"

mkdir -p "$APP_DIR"

for file in flight_monitor.py config.example.json README.md requirements.txt; do
  if [ ! -e "$APP_DIR/$file" ] && [ -e "$SEED_DIR/$file" ]; then
    cp "$SEED_DIR/$file" "$APP_DIR/$file"
  fi
done

exec "$@"
