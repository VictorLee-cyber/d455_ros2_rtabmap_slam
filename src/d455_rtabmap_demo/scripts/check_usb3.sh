#!/bin/bash

echo "========== RealSense USB Check =========="

if ! command -v rs-enumerate-devices &> /dev/null; then
    echo "[ERROR] rs-enumerate-devices not found."
    echo "Please install librealsense2-utils:"
    echo "  sudo apt install librealsense2-utils"
    exit 1
fi

DEVICE_INFO=$(rs-enumerate-devices 2>/dev/null)

if [ -z "$DEVICE_INFO" ]; then
    echo "[ERROR] No RealSense device detected."
    echo "Please check USB cable, USB port, or VMware USB passthrough."
    exit 1
fi

echo "$DEVICE_INFO" | grep "Name\|Serial Number\|Firmware Version\|Usb Type"

echo ""
echo "========== USB Tree =========="
lsusb -t

echo ""
USB_TYPE=$(echo "$DEVICE_INFO" | grep "Usb Type" | awk -F ':' '{print $2}' | xargs)

if [[ "$USB_TYPE" == 3* ]]; then
    echo "[OK] RealSense is running in USB3 mode: $USB_TYPE"
else
    echo "[WARN] RealSense is not running in USB3 mode: $USB_TYPE"
    echo ""
    echo "Suggestions:"
    echo "  1. Use a real USB3 data cable."
    echo "  2. Avoid USB hubs or docking stations."
    echo "  3. Use a USB3 port directly on the PC."
    echo "  4. If using VMware, enable USB 3.1 controller."
fi
