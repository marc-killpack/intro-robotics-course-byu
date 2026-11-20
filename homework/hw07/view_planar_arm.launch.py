"""Provided HW07 launch: show homework/hw07/planar_arm.urdf in RViz.

Make planar_arm.urdf first (problem 5(a)). Then, from /workspace in the
course container, start this launch file, your arm node, and the path
publisher in three shells:

    ros2 launch homework/hw07/view_planar_arm.launch.py
    python3 -m homework.hw07.arm_node
    python3 -m homework.hw07.path_publisher

The joint and robot-description topics are moved under /hw07 so this model
does not interfere with the R2D2 model that the container starts. TF stays
global, so tf2_echo sees the arm frames directly.
"""

from pathlib import Path

from launch import LaunchDescription
from launch_ros.actions import Node

HERE = Path(__file__).resolve().parent
URDF = HERE / "planar_arm.urdf"
REMAPS = [
    ("joint_states", "/hw07/joint_states"),
    ("robot_description", "/hw07/robot_description"),
]


def generate_launch_description():
    if not URDF.exists():
        raise FileNotFoundError(
            f"{URDF} is missing. Copy your homework/hw04/arm.urdf to this name "
            "and make the problem 5(a) edits first."
        )
    return LaunchDescription(
        [
            Node(
                package="robot_state_publisher",
                executable="robot_state_publisher",
                name="hw07_state_publisher",
                parameters=[{"robot_description": URDF.read_text()}],
                remappings=REMAPS,
            ),
            Node(
                package="rviz2",
                executable="rviz2",
                name="hw07_rviz",
                arguments=["-d", str(HERE / "planar_arm.rviz")],
            ),
        ]
    )
