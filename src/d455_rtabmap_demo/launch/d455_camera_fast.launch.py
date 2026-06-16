from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    realsense_launch = PathJoinSubstitution([
        FindPackageShare('realsense2_camera'),
        'launch',
        'rs_launch.py'
    ])

    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(realsense_launch),
            launch_arguments={
                'enable_color': 'true',
                'enable_depth': 'true',
                'align_depth.enable': 'true',
                'enable_sync': 'true',

                # Do not publish RealSense point cloud.
                # RTAB-Map will generate point cloud internally from RGB + Depth.
                'pointcloud.enable': 'false',

                # IMU is disabled for the basic RGB-D SLAM demo.
                'enable_gyro': 'false',
                'enable_accel': 'false',

                # Fast mode: lower resolution, higher frame rate.
                # Suitable for VMware or low-performance PCs.
                'rgb_camera.color_profile': '424x240x30',
                'depth_module.depth_profile': '480x270x30',
            }.items()
        )
    ])
