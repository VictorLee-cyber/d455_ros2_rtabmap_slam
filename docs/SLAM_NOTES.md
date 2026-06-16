# D455 RGB-D SLAM Notes

This document explains the basic principle, software dependencies, ROS2 topics, launch parameters, and common issues of this project.

本项目基于 Intel RealSense D455、ROS2 Humble 和 RTAB-Map，实现一个可复现的 RGB-D SLAM 建图 Demo。项目重点不是从零实现 SLAM 算法，而是完成 D455 相机接入、RGB-D 数据同步、RTAB-Map 建图配置、地图保存和工程问题排查。

---

## 1. Project Overview

System pipeline:

```text
Intel RealSense D455
        ↓
realsense2_camera
        ↓
RGB Image / Aligned Depth Image / CameraInfo
        ↓
RTAB-Map RGB-D SLAM
        ↓
Visual Odometry / 3D Map / 2D Occupancy Grid
        ↓
RTAB-Map Database / Nav2 Map Export
```


```text
D455 相机负责提供 RGB 图像和深度图
realsense2_camera 负责把相机数据发布到 ROS2
RTAB-Map 负责根据 RGB-D 数据估计轨迹并构建地图
Nav2 map_saver 可用于导出 2D 栅格地图
```

---

## 2. Why Use RTAB-Map Instead of FAST-LIO?

FAST-LIO / FAST-LIO2 is designed for LiDAR-Inertial Odometry, usually using LiDAR point cloud and IMU data.

D455 is an RGB-D camera. Although it can publish `PointCloud2`, the point cloud is generated from depth image projection, not from a real LiDAR scan.

Therefore:

```text
D455 + RTAB-Map      → recommended for RGB-D SLAM
Mid360 + FAST-LIO2   → recommended for LiDAR SLAM
D455 + Nav2          → suitable for near-field obstacle avoidance
```

In this project, D455 is used as an RGB-D camera, and RTAB-Map is used as the SLAM backend.

---

## 3. Software Dependencies

Tested environment:

```text
Ubuntu 22.04
ROS2 Humble
Intel RealSense D455
RTAB-Map ROS
Nav2 map server
```

Install ROS2 dependencies:

```bash
sudo apt update
sudo apt install -y ros-humble-realsense2-*
sudo apt install -y ros-humble-rtabmap-ros
sudo apt install -y ros-humble-nav2-map-server
```

Install RealSense tools:

```bash
sudo apt install -y librealsense2-utils
```

Optional tool for viewing RTAB-Map databases:

```bash
sudo apt install -y rtabmap
```

Useful check commands:

```bash
ros2 pkg list | grep realsense
ros2 pkg list | grep rtabmap
rs-enumerate-devices
lsusb -t
```

---

## 4. RealSense D455 ROS2 Topics

After launching D455, the key topics are:

```text
/camera/camera/color/image_raw
/camera/camera/color/camera_info
/camera/camera/aligned_depth_to_color/image_raw
/camera/camera/depth/image_rect_raw
/camera/camera/extrinsics/depth_to_color
```

RTAB-Map mainly uses:

```text
RGB topic:
  /camera/camera/color/image_raw

Depth topic:
  /camera/camera/aligned_depth_to_color/image_raw

Camera info topic:
  /camera/camera/color/camera_info
```

Check topic frequency:

```bash
ros2 topic hz /camera/camera/color/image_raw
ros2 topic hz /camera/camera/aligned_depth_to_color/image_raw
```

Check frame id:

```bash
ros2 topic echo /camera/camera/color/camera_info --once | grep frame_id
```

Common output:

```text
frame_id: camera_color_optical_frame
```

In this project, RTAB-Map uses:

```text
frame_id: camera_link
```

This is more suitable for ground robot style mapping and avoids confusion caused by optical frame orientation.

---

## 5. Camera Launch Modes

This project provides two D455 launch modes.

### Fast Mode

Suitable for VMware or low-performance computers.

```text
RGB:   424x240 @ 30Hz
Depth: 480x270 @ 30Hz
```

Launch command:

```bash
ros2 launch d455_rtabmap_demo d455_camera_fast.launch.py
```

Use this mode when:

```text
The system is slow
RTAB-Map loses tracking easily
You want a smoother demo
You are running inside VMware
```

### Balanced Mode

Suitable for better visual quality.

```text
RGB:   640x480 @ 15Hz
Depth: 640x480 @ 15Hz
```

Launch command:

```bash
ros2 launch d455_rtabmap_demo d455_camera_balanced.launch.py
```

Use this mode when:

```text
USB3 is stable
The computer has enough performance
You want better map quality
```

---

## 6. RTAB-Map Launch Parameters

Launch command:

```bash
ros2 launch d455_rtabmap_demo rtabmap_d455.launch.py
```

Important parameters:

```text
frame_id:=camera_link
```

Use `camera_link` as the base camera frame.

```text
approx_sync:=true
```

RGB and depth images may not arrive at exactly the same timestamp, especially in VMware. Approximate synchronization improves robustness.

```text
visual_odometry:=true
```

RTAB-Map uses visual odometry to estimate camera motion.

```text
qos:=2
```

RealSense image topics usually use sensor data QoS. This parameter helps RTAB-Map subscribe correctly.

```text
delete_db_on_start:=true
```

A new RTAB-Map database is created each time. If you want to continue a previous map, set it to `false`.

```text
--Reg/Force3DoF true
```

For ground robot applications, motion is usually limited to x, y, and yaw. This parameter reduces map tilt caused by roll and pitch drift.

```text
--Rtabmap/DetectionRate 2
```

Limits RTAB-Map processing rate to reduce CPU load.

```text
--Vis/MaxFeatures 800
--Kp/MaxFeatures 800
```

Limits the number of visual features and keypoints to balance tracking quality and speed.

---

## 7. USB3 Check

D455 should run in USB3 mode.

Check USB type:

```bash
rs-enumerate-devices | grep "Usb Type"
```

Expected result:

```text
Usb Type Descriptor : 3.x
```

Check USB tree:

```bash
lsusb -t
```

Expected result:

```text
Driver=xhci_hcd, 5000M
```

If the output shows:

```text
Usb Type Descriptor : 2.1
Driver=ehci-pci, 480M
```

then D455 is running in USB2 mode. This may cause frame drops, low FPS, or device disconnection.

Solutions:

```text
Use a real USB3 data cable
Use a USB3 port directly on the PC
Avoid USB hubs or docking stations
For VMware, enable USB 3.1 controller
Reconnect the camera to the virtual machine
```

Project script:

```bash
ros2 run d455_rtabmap_demo check_usb3.sh
```

---

## 8. RTAB-Map Database

By default, RTAB-Map stores the mapping database at:

```bash
~/.ros/rtabmap.db
```

The database contains:

```text
Keyframes
Camera trajectory
RGB images
Depth images
Visual features
Graph structure
Loop closure information
```

Save current database:

```bash
ros2 run d455_rtabmap_demo save_rtabmap_db.sh
```

Open database:

```bash
ros2 run d455_rtabmap_demo open_rtabmap_db.sh
```

Open a specific database:

```bash
ros2 run d455_rtabmap_demo open_rtabmap_db.sh ~/rtabmap_maps/example.db
```

---

## 9. Export 2D Map for Nav2

RTAB-Map can publish a 2D occupancy grid on `/map`.

Save the 2D map:

```bash
ros2 run d455_rtabmap_demo save_2d_map.sh
```

The output files are usually:

```text
~/maps/d455_map_xxxxx.yaml
~/maps/d455_map_xxxxx.pgm
```

These files can be used later by Nav2 for navigation.

---

## 10. Common Issues

### 10.1 Package 'realsense2_camera' not found

Reason:

```text
RealSense ROS2 wrapper is not installed.
```

Solution:

```bash
sudo apt install -y ros-humble-realsense2-*
```

---

### 10.2 xioctl(VIDIOC_QBUF) failed, No such device

Reason:

```text
D455 disconnected during streaming.
This is often caused by USB2 mode, bad cable, unstable USB hub, or high bandwidth pressure.
```

Solution:

```text
Use USB3 mode
Change USB cable
Avoid USB hub
Lower resolution
Disable pointcloud and IMU
```

---

### 10.3 Map is tilted

Reason:

```text
RTAB-Map estimates full 6DoF motion, or the optical frame is used incorrectly.
```

Solution:

```text
Use frame_id:=camera_link
Enable --Reg/Force3DoF true
Move the camera smoothly
Avoid dynamic objects
```

---

### 10.4 RTAB-Map is very slow

Reason:

```text
High resolution
Too many features
RViz and rtabmap_viz both running
Large point cloud visualization
VMware performance overhead
```

Solution:

```text
Use fast mode
Disable RViz
Reduce DetectionRate
Reduce MaxFeatures
Avoid showing dense 3D map continuously
```

---

### 10.5 Camera must move very slowly

Reason:

```text
Visual SLAM relies on feature matching between adjacent frames.
If the camera moves too fast, image overlap becomes small and tracking may fail.
```

Solution:

```text
Use 30Hz fast mode
Move smoothly
Avoid quick rotation
Keep enough texture in the image
Avoid white walls, screens, reflections, and moving people
```

---

## 11. Recommended Testing Process

Step 1: Check USB3

```bash
ros2 run d455_rtabmap_demo check_usb3.sh
```

Step 2: Launch D455

```bash
ros2 launch d455_rtabmap_demo d455_camera_fast.launch.py
```

Step 3: Check topics

```bash
ros2 topic list | grep camera
ros2 topic hz /camera/camera/color/image_raw
ros2 topic hz /camera/camera/aligned_depth_to_color/image_raw
```

Step 4: Launch RTAB-Map

```bash
ros2 launch d455_rtabmap_demo rtabmap_d455.launch.py
```

Step 5: Move camera slowly

Recommended scenes:

```text
Corners
Tables
Chairs
Cabinets
Door frames
Textured floor
```

Avoid:

```text
White walls
Reflective screens
Moving people
Fast rotations
Low-light environments
```

Step 6: Save database

```bash
ros2 run d455_rtabmap_demo save_rtabmap_db.sh
```

Step 7: Export 2D map

```bash
ros2 run d455_rtabmap_demo save_2d_map.sh
```

---

## 12. Future Work

Possible extensions:

```text
D455 + depthimage_to_laserscan for obstacle avoidance
D455 + Nav2 for RGB-D navigation
Mid360 + FAST-LIO2 for LiDAR SLAM
D455 + Mid360 multi-sensor fusion
A2 robot integration
```

This project can be used as the first step toward a complete robot perception and navigation system.
