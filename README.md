# D455 ROS2 RTAB-Map SLAM

A simple RGB-D SLAM demo using **Intel RealSense D455**, **ROS2 Humble**, and **RTAB-Map**.

This project provides launch files and utility scripts for D455 camera startup, RGB-D SLAM mapping, database saving, and 2D map export.

---

## 1. Environment

Tested on:

```text
Ubuntu 22.04
ROS2 Humble
Intel RealSense D455
RTAB-Map ROS
```

---

## 2. Install Dependencies

```bash
sudo apt update
sudo apt install -y ros-humble-realsense2-*
sudo apt install -y ros-humble-rtabmap-ros
sudo apt install -y ros-humble-nav2-map-server
sudo apt install -y librealsense2-utils
sudo apt install -y rtabmap
```

---

## 3. Build

```bash
cd ~/projects/d455_ros2_rtabmap_slam

rosdep install --from-paths src --ignore-src -r -y

colcon build --symlink-install

source install/setup.bash
```

---

## 4. Check D455 USB Mode

D455 should run in USB3 mode.

```bash
ros2 run d455_rtabmap_demo check_usb3.sh
```

Expected result:

```text
Usb Type Descriptor : 3.x
Driver=xhci_hcd, 5000M
```

If it shows USB2, change the USB cable, USB port, or VMware USB settings.

---

## 5. Launch D455 Camera

### Fast Mode

Recommended for VMware or low-performance PCs.

```bash
ros2 launch d455_rtabmap_demo d455_camera_fast.launch.py
```

### Balanced Mode

Recommended for better image quality.

```bash
ros2 launch d455_rtabmap_demo d455_camera_balanced.launch.py
```

---

## 6. Check Camera Topics

Open a new terminal:

```bash
source ~/projects/d455_ros2_rtabmap_slam/install/setup.bash

ros2 topic list | grep camera
```

Key topics:

```text
/camera/camera/color/image_raw
/camera/camera/color/camera_info
/camera/camera/aligned_depth_to_color/image_raw
```

Check frequency:

```bash
ros2 topic hz /camera/camera/color/image_raw
ros2 topic hz /camera/camera/aligned_depth_to_color/image_raw
```

---

## 7. Launch RTAB-Map SLAM

Open a new terminal:

```bash
source ~/projects/d455_ros2_rtabmap_slam/install/setup.bash

ros2 launch d455_rtabmap_demo rtabmap_d455.launch.py
```

Move the camera slowly and smoothly.

Recommended scenes:

```text
Corners
Tables
Chairs
Cabinets
Door frames
Textured floors
```

Avoid:

```text
White walls
Reflective screens
Moving people
Fast rotation
Low light
```

---

## 8. Save RTAB-Map Database

Default database path:

```text
~/.ros/rtabmap.db
```

Save current database:

```bash
ros2 run d455_rtabmap_demo save_rtabmap_db.sh
```

Saved files will be placed in:

```text
~/rtabmap_maps/
```

---

## 9. Open RTAB-Map Database

Open default database:

```bash
ros2 run d455_rtabmap_demo open_rtabmap_db.sh
```

Open a specific database:

```bash
ros2 run d455_rtabmap_demo open_rtabmap_db.sh ~/rtabmap_maps/example.db
```

---

## 10. Export 2D Map

If `/map` is being published, save the 2D occupancy grid map:

```bash
ros2 run d455_rtabmap_demo save_2d_map.sh
```

Output path:

```text
~/maps/
```

Generated files:

```text
d455_map_xxxxx.yaml
d455_map_xxxxx.pgm
```

---

## 11. Notes

More detailed notes:

```text
docs/SLAM_NOTES_CN.md
docs/SLAM_NOTES_EN.md
```

---

## 12. Common Issues

### D455 is running in USB2 mode

Check:

```bash
rs-enumerate-devices | grep "Usb Type"
lsusb -t
```

Use a USB3 cable and USB3 port.

### RTAB-Map is slow

Use fast mode:

```bash
ros2 launch d455_rtabmap_demo d455_camera_fast.launch.py
```

Also avoid running RViz and dense 3D visualization at the same time.

### Map is tilted

This project uses:

```text
frame_id:=camera_link
--Reg/Force3DoF true
```

This helps reduce map tilt for ground robot-style movement.

---

## License

MIT License
