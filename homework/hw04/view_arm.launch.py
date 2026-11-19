"""Provided HW04 launch: show homework/hw04/arm.urdf in its own RViz window.

Run from /workspace in the course container:

    ros2 launch homework/hw04/view_arm.launch.py

The joint and robot-description topics are moved under /hw04 so this model
does not interfere with the R2D2 model that the container starts. TF stays
global, so tf2_echo and the comparison script see the arm frames directly.
"""

from pathlib import Path

from launch import LaunchDescription
from launch_ros.actions import Node

HERE = Path(__file__).resolve().parent
URDF = HERE / "arm.urdf"
REMAPS = [
    ("joint_states", "/hw04/joint_states"),
    ("robot_description", "/hw04/robot_description"),
]


def generate_launch_description():
    return LaunchDescription(
        [
            Node(
                package="robot_state_publisher",
                executable="robot_state_publisher",
                name="hw04_state_publisher",
                parameters=[{"robot_description": URDF.read_text()}],
                remappings=REMAPS,
            ),
            Node(
                package="joint_state_publisher_gui",
                executable="joint_state_publisher_gui",
                name="hw04_joint_sliders",
                arguments=[str(URDF)],
                remappings=REMAPS,
            ),
            Node(
                package="rviz2",
                executable="rviz2",
                name="hw04_rviz",
                arguments=["-d", str(HERE / "arm.rviz")],
            ),
        ]
    )
