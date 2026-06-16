# D455 RGB-D SLAM 笔记

本文档记录本项目的基本原理、软件依赖、ROS2 话题关系、RTAB-Map 参数含义以及常见问题排查。

本项目基于 Intel RealSense D455、ROS2 Humble 和 RTAB-Map，实现一个可复现的 RGB-D SLAM 建图 Demo。项目重点不是从零实现 SLAM 算法，而是完成 D455 相机接入、RGB-D 数据同步、RTAB-Map 建图配置、地图保存和工程问题排查。

---

## 1. 项目整体流程

```text
Intel RealSense D455
        ↓
realsense2_camera
        ↓
RGB 图像 / 对齐深度图 / CameraInfo
        ↓
RTAB-Map RGB-D SLAM
        ↓
视觉里程计 / 三维点云地图 / 二维栅格地图
        ↓
RTAB-Map 数据库 / Nav2 地图导出
```

D455 负责提供 RGB 图像和深度图；`realsense2_camera` 负责将相机数据发布到 ROS2；RTAB-Map 根据 RGB-D 数据估计相机运动并构建地图；后续可通过 `nav2_map_server` 导出 2D 栅格地图。

---

## 2. 为什么使用 RTAB-Map 而不是 FAST-LIO

FAST-LIO / FAST-LIO2 主要面向 LiDAR-Inertial Odometry，即激光雷达点云与 IMU 的紧耦合定位建图。

D455 是 RGB-D 相机，虽然可以发布 `PointCloud2`，但这个点云是由深度图反投影生成的，不是真正的激光雷达扫描点云。因此本项目采用 RTAB-Map 做 RGB-D SLAM。

推荐组合：

```text
D455 + RTAB-Map      → RGB-D SLAM 建图
Mid360 + FAST-LIO2   → 激光雷达 SLAM 建图
D455 + Nav2          → 近场避障和视觉辅助导航
```

---

## 3. 软件依赖

测试环境：

```text
Ubuntu 22.04
ROS2 Humble
Intel RealSense D455
RTAB-Map ROS
Nav2 map server
```

安装依赖：

```bash
sudo apt update
sudo apt install -y ros-humble-realsense2-*
sudo apt install -y ros-humble-rtabmap-ros
sudo apt install -y ros-humble-nav2-map-server
sudo apt install -y librealsense2-utils
```

可选安装 RTAB-Map 数据库查看工具：

```bash
sudo apt install -y rtabmap
```

检查依赖是否安装成功：

```bash
ros2 pkg list | grep realsense
ros2 pkg list | grep rtabmap
rs-enumerate-devices
lsusb -t
```

---

## 4. D455 关键 ROS2 话题

启动 D455 后，常用话题包括：

```text
/camera/camera/color/image_raw
/camera/camera/color/camera_info
/camera/camera/aligned_depth_to_color/image_raw
/camera/camera/depth/image_rect_raw
/camera/camera/extrinsics/depth_to_color
```

RTAB-Map 主要使用：

```text
RGB 图像：
/camera/camera/color/image_raw

对齐深度图：
/camera/camera/aligned_depth_to_color/image_raw

相机内参：
/camera/camera/color/camera_info
```

检查频率：

```bash
ros2 topic hz /camera/camera/color/image_raw
ros2 topic hz /camera/camera/aligned_depth_to_color/image_raw
```

查看坐标系：

```bash
ros2 topic echo /camera/camera/color/camera_info --once | grep frame_id
```

本项目在 RTAB-Map 中使用：

```text
frame_id:=camera_link
```

这样更适合地面机器人建图，避免直接使用 `camera_color_optical_frame` 时出现地图方向理解混乱的问题。

---

## 5. 相机启动模式

### Fast 模式

适合虚拟机或性能一般的电脑：

```text
RGB:   424x240 @ 30Hz
Depth: 480x270 @ 30Hz
```

启动命令：

```bash
ros2 launch d455_rtabmap_demo d455_camera_fast.launch.py
```

适合场景：

```text
系统较卡
虚拟机环境
需要提高跟踪流畅度
移动时容易丢跟踪
```

### Balanced 模式

适合效果展示：

```text
RGB:   640x480 @ 15Hz
Depth: 640x480 @ 15Hz
```

启动命令：

```bash
ros2 launch d455_rtabmap_demo d455_camera_balanced.launch.py
```

适合场景：

```text
USB3 稳定
电脑性能较好
需要更清晰的建图效果
```

---

## 6. RTAB-Map 启动与参数说明

启动建图：

```bash
ros2 launch d455_rtabmap_demo rtabmap_d455.launch.py
```

关键参数：

```text
frame_id:=camera_link
```

使用相机主体坐标系，适合地面机器人场景。

```text
approx_sync:=true
```

RGB 和 Depth 时间戳不一定完全一致，近似同步可以提高稳定性。

```text
visual_odometry:=true
```

启用 RTAB-Map 视觉里程计。

```text
qos:=2
```

适配 RealSense 图像话题常用的 sensor data QoS。

```text
delete_db_on_start:=true
```

每次启动时清空旧地图并重新建图。需要继续使用旧地图时应改为 `false`。

```text
--Reg/Force3DoF true
```

限制为地面机器人常见的平面运动，减少 roll / pitch 漂移导致的地图倾斜。

```text
--Rtabmap/DetectionRate 2
```

限制 RTAB-Map 处理频率，降低计算负载。

```text
--Vis/MaxFeatures 800
--Kp/MaxFeatures 800
```

限制视觉特征点数量，在跟踪效果和运行速度之间取得平衡。

---

## 7. USB3 检查

D455 应尽量工作在 USB3 模式。

检查 USB 类型：

```bash
rs-enumerate-devices | grep "Usb Type"
```

正常结果：

```text
Usb Type Descriptor : 3.x
```

检查 USB 树：

```bash
lsusb -t
```

正常结果应包含：

```text
Driver=xhci_hcd, 5000M
```

异常情况：

```text
Usb Type Descriptor : 2.1
Driver=ehci-pci, 480M
```

这说明 D455 运行在 USB2 模式，可能导致掉帧、低帧率、设备掉线等问题。

项目内置检查脚本：

```bash
ros2 run d455_rtabmap_demo check_usb3.sh
```

常见解决方法：

```text
更换真正支持 USB3 数据传输的数据线
直接连接电脑 USB3 接口
避免扩展坞和 USB Hub
VMware 中启用 USB 3.1 控制器
重新将 D455 连接到虚拟机
```

---

## 8. RTAB-Map 数据库

默认数据库路径：

```bash
~/.ros/rtabmap.db
```

数据库中保存：

```text
关键帧
相机轨迹
RGB 图像
深度图
视觉特征
图优化结构
回环检测信息
```

保存当前数据库：

```bash
ros2 run d455_rtabmap_demo save_rtabmap_db.sh
```

打开默认数据库：

```bash
ros2 run d455_rtabmap_demo open_rtabmap_db.sh
```

打开指定数据库：

```bash
ros2 run d455_rtabmap_demo open_rtabmap_db.sh ~/rtabmap_maps/example.db
```

---

## 9. 导出 Nav2 可用的 2D 地图

RTAB-Map 可发布 `/map` 二维栅格地图。保存地图：

```bash
ros2 run d455_rtabmap_demo save_2d_map.sh
```

输出文件一般位于：

```text
~/maps/d455_map_xxxxx.yaml
~/maps/d455_map_xxxxx.pgm
```

这些文件后续可用于 Nav2 导航。

---

## 10. 常见问题

### 10.1 Package 'realsense2_camera' not found

原因：未安装 RealSense ROS2 wrapper。

解决：

```bash
sudo apt install -y ros-humble-realsense2-*
```

### 10.2 xioctl(VIDIOC_QBUF) failed, No such device

原因：相机取流过程中掉线，常见于 USB2、线材不稳定、带宽不足。

解决：

```text
切换 USB3
更换 USB3 数据线
避免 USB Hub
降低分辨率
关闭 pointcloud 和 IMU
```

### 10.3 地图倾斜

原因：使用光学坐标系或视觉里程计估计 6DoF 运动时出现 roll / pitch 漂移。

解决：

```text
frame_id 使用 camera_link
开启 --Reg/Force3DoF true
相机平稳移动
避开动态目标
```

### 10.4 RTAB-Map 很卡

原因：

```text
分辨率过高
特征点过多
RViz 和 rtabmap_viz 同时开启
三维点云显示负载过高
虚拟机性能开销
```

解决：

```text
使用 fast 模式
关闭 RViz
降低 DetectionRate
降低 MaxFeatures
减少长时间显示密集三维点云
```

### 10.5 相机必须移动很慢

原因：视觉 SLAM 依赖相邻帧的特征匹配，移动过快会导致图像重叠区域不足。

解决：

```text
使用 30Hz fast 模式
平稳移动
避免快速旋转
保持画面中有足够纹理
避开白墙、屏幕、反光区域和动态人物
```

---

## 11. 推荐测试流程

检查 USB3：

```bash
ros2 run d455_rtabmap_demo check_usb3.sh
```

启动 D455：

```bash
ros2 launch d455_rtabmap_demo d455_camera_fast.launch.py
```

检查话题：

```bash
ros2 topic list | grep camera
ros2 topic hz /camera/camera/color/image_raw
ros2 topic hz /camera/camera/aligned_depth_to_color/image_raw
```

启动 RTAB-Map：

```bash
ros2 launch d455_rtabmap_demo rtabmap_d455.launch.py
```

推荐测试场景：

```text
墙角
桌椅
柜子
门框
地面纹理
固定物体
```

应避免：

```text
纯白墙
反光屏幕
移动人物
快速旋转
弱光环境
```

保存数据库：

```bash
ros2 run d455_rtabmap_demo save_rtabmap_db.sh
```

导出 2D 地图：

```bash
ros2 run d455_rtabmap_demo save_2d_map.sh
```

---

## 12. 后续扩展方向

```text
D455 + depthimage_to_laserscan 近场避障
D455 + Nav2 视觉辅助导航
Mid360 + FAST-LIO2 激光 SLAM
D455 + Mid360 多传感器融合
A2 机器人平台集成
```

本项目可以作为机器人感知与导航系统的第一步工程基础。
