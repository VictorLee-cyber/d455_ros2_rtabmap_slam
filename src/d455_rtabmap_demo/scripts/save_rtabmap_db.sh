#!/bin/bash

SAVE_DIR="$HOME/rtabmap_maps"
SRC_DB="$HOME/.ros/rtabmap.db"

mkdir -p "$SAVE_DIR"

TIME=$(date +%Y%m%d_%H%M%S)
DST_DB="$SAVE_DIR/d455_rtabmap_$TIME.db"

if [ ! -f "$SRC_DB" ]; then
    echo "[ERROR] RTAB-Map database not found: $SRC_DB"
    echo "Please run RTAB-Map SLAM first."
    exit 1
fi

cp "$SRC_DB" "$DST_DB"

echo "[OK] RTAB-Map database saved."
echo "Source: $SRC_DB"
echo "Target: $DST_DB"
