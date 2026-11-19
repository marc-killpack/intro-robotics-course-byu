from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    package_dir = Path(get_package_share_directory("r2d2_demo"))
    urdf = (package_dir / "urdf" / "r2d2.urdf").read_text()
    rviz_config = str(package_dir / "rviz" / "r2d2.rviz")

    return LaunchDescription(
        [
            DeclareLaunchArgument("use_joint_gui", default_value="true"),
            Node(
                package="robot_state_publisher",
                executable="robot_state_publisher",
                parameters=[{"robot_description": urdf}],
            ),
            Node(
                package="joint_state_publisher_gui",
                executable="joint_state_publisher_gui",
                condition=IfCondition(LaunchConfiguration("use_joint_gui")),
            ),
            Node(
                package="rviz2",
                executable="rviz2",
                arguments=["-d", rviz_config],
            ),
        ]
    )
