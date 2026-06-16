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

                # Keep RealSense point cloud disabled to reduce CPU/GPU load.
                'pointcloud.enable': 'false',

                # IMU is disabled in this demo.
                'enable_gyro': 'false',
                'enable_accel': 'false',

                # Balanced mode: better image quality with acceptable performance.
                'rgb_camera.color_profile': '640x480x15',
                'depth_module.depth_profile': '640x480x15',
            }.items()
        )
    ])
