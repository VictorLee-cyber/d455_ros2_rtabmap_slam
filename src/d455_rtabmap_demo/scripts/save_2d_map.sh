#!/bin/bash

SAVE_DIR="$HOME/maps"
mkdir -p "$SAVE_DIR"

TIME=$(date +%Y%m%d_%H%M%S)
MAP_NAME="$SAVE_DIR/d455_map_$TIME"

if ! command -v ros2 &> /dev/null; then
    echo "[ERROR] ros2 command not found. Please source ROS2 first."
    exit 1
fi

echo "[INFO] Saving 2D occupancy grid map..."
echo "[INFO] Target: $MAP_NAME"

ros2 run nav2_map_server map_saver_cli -f "$MAP_NAME"

if [ -f "$MAP_NAME.yaml" ] && [ -f "$MAP_NAME.pgm" ]; then
    echo "[OK] 2D map saved:"
    echo "  $MAP_NAME.yaml"
    echo "  $MAP_NAME.pgm"
else
    echo "[WARN] Map save command finished, but output files were not found."
    echo "Please check whether /map topic is being published."
fi
