"""Provided launch file: run the conveyor project live in ROS and RViz.

From /workspace in the course container:

    ros2 launch homework/project/project.launch.py
    ros2 launch homework/project/project.launch.py scenario:=s2 seed:=22
    ros2 launch homework/project/project.launch.py \
        controller:=homework.project.my_controller:MyController realism:=on
    ros2 launch homework/project/project.launch.py rate:=0.5 rviz:=false

It starts four nodes under the /project namespace: the simulator and camera
nodes (one process), robot_state_publisher with the scenario's arm, the
controller node that runs your Controller class, and RViz. Live runs are for
watching and demonstrating; scores come from homework/project/run.py, which
does not depend on your computer's speed. Lower rate if step() cannot keep up.
"""

from pathlib import Path
import subprocess

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
NAMESPACE = "project"
ARGUMENTS = {
    "scenario": ("s1", "scenario name (s1, s2, s3) or path of a .toml file"),
    "seed": ("", "episode seed (default: the scenario's)"),
    "controller": ("homework.project.my_controller:MyController", "module:Class to run"),
    "realism": ("", "on or off (default: the scenario's setting)"),
    "rate": ("1.0", "real-time factor; 0.5 runs at half speed"),
    "rviz": ("true", "start RViz"),
    "truth_markers": ("false", "faculty demonstration: show object truth in RViz"),
}


def nodes(context):
    value = {name: LaunchConfiguration(name).perform(context) for name in ARGUMENTS}
    # The course package needs the virtual environment's Python (OpenCV), not
    # the system Python that runs ros2 launch, so ask it for the URDF.
    urdf = subprocess.run(
        ["python3", "-m", "intro_robotics.project.ros_bridge", value["scenario"]],
        cwd=ROOT, check=True, capture_output=True, text=True,
    ).stdout
    ros_args = ["--ros-args", "-r", f"__ns:=/{NAMESPACE}"]
    sim = ["python3", "-m", "intro_robotics.project.sim_node", "--scenario", value["scenario"],
           "--rate", value["rate"]]
    if value["seed"]:
        sim += ["--seed", value["seed"]]
    if value["realism"]:
        sim += ["--realism", value["realism"]]
    if value["truth_markers"].lower() == "true":
        sim += ["--truth-markers"]
    actions = [
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            namespace=NAMESPACE,
            # TF at the control rate (the default is 20 Hz, which lags the arm).
            parameters=[{"robot_description": urdf, "use_sim_time": True, "publish_frequency": 50.0}],
        ),
        ExecuteProcess(cmd=sim + ros_args, cwd=str(ROOT), output="screen", name="conveyor_sim"),
        ExecuteProcess(
            cmd=["python3", "-m", "intro_robotics.project.controller_node", "--scenario", value["scenario"],
                 "--controller", value["controller"], *ros_args],
            cwd=str(ROOT), output="screen", name="project_controller",
        ),
    ]
    if value["rviz"].lower() == "true":
        actions.append(Node(package="rviz2", executable="rviz2", name="project_rviz",
                            arguments=["-d", str(HERE / "project.rviz")],
                            parameters=[{"use_sim_time": True}]))
    return actions


def generate_launch_description():
    declared = [DeclareLaunchArgument(name, default_value=default, description=text)
                for name, (default, text) in ARGUMENTS.items()]
    return LaunchDescription([*declared, OpaqueFunction(function=nodes)])
