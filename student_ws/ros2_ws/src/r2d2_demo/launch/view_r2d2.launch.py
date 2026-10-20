from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    package_dir = Path(get_package_share_directory("r2d2_demo"))
    urdf = (package_dir / "urdf" / "r2d2.urdf").read_text()
    rviz_config = str(package_dir / "rviz" / "r2d2.rviz")

    return LaunchDescription([
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            parameters=[{"robot_description": urdf}],
        ),
        Node(
            package="joint_state_publisher_gui",
            executable="joint_state_publisher_gui",
        ),
        Node(
            package="rviz2",
            executable="rviz2",
            arguments=["-d", rviz_config],
        ),
    ])
