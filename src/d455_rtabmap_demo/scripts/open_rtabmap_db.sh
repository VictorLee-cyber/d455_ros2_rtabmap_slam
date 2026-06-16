#!/bin/bash

DB_PATH=${1:-"$HOME/.ros/rtabmap.db"}

if [ ! -f "$DB_PATH" ]; then
    echo "[ERROR] Database not found: $DB_PATH"
    echo ""
    echo "Usage:"
    echo "  ros2 run d455_rtabmap_demo open_rtabmap_db.sh"
    echo "  ros2 run d455_rtabmap_demo open_rtabmap_db.sh /path/to/rtabmap.db"
    exit 1
fi

if ! command -v rtabmap-databaseViewer &> /dev/null; then
    echo "[ERROR] rtabmap-databaseViewer not found."
    echo "Please install RTAB-Map tools:"
    echo "  sudo apt install rtabmap"
    exit 1
fi

echo "[INFO] Opening RTAB-Map database: $DB_PATH"
rtabmap-databaseViewer "$DB_PATH"
