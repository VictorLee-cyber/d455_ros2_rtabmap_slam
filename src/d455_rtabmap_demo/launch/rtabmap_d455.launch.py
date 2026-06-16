from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    rtabmap_launch = PathJoinSubstitution([
        FindPackageShare('rtabmap_launch'),
        'launch',
        'rtabmap.launch.py'
    ])

    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(rtabmap_launch),
            launch_arguments={
                # RealSense D455 RGB-D topics
                'rgb_topic': '/camera/camera/color/image_raw',
                'depth_topic': '/camera/camera/aligned_depth_to_color/image_raw',
                'camera_info_topic': '/camera/camera/color/camera_info',

                # Use camera_link instead of optical frame to avoid confusing map orientation.
                'frame_id': 'camera_link',

                # RGB and depth may not be strictly synchronized, especially in VMware.
                'approx_sync': 'true',

                # Use RTAB-Map visual odometry.
                'visual_odometry': 'true',

                # RViz is disabled by default to reduce load.
                'rviz': 'false',
                'rtabmap_viz': 'true',

                # RealSense image topics usually require sensor-data QoS.
                'qos': '2',

                # Start a new database every time.
                # Change to false if you want to continue the previous map.
                'delete_db_on_start': 'true',

                # Practical parameters for ground robot RGB-D SLAM.
                # Force3DoF reduces map tilt for ground-plane motion.
                'args': (
                    '--Reg/Force3DoF true '
                    '--Rtabmap/DetectionRate 2 '
                    '--Vis/MaxFeatures 800 '
                    '--Kp/MaxFeatures 800 '
                    '--RGBD/LinearUpdate 0.08 '
                    '--RGBD/AngularUpdate 0.08'
                ),
            }.items()
        )
    ])
