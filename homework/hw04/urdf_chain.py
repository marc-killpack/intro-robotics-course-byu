"""Provided offline URDF reader for HW04 problem 5 (no ROS needed).

It follows the joints from one link back to the root, the way ROS's
robot_state_publisher builds TF: each joint contributes its fixed origin
(xyz, then roll-pitch-yaw) followed by its motion about its axis. The public
check uses it to compare your URDF with your SerialArm.fk.
"""

from pathlib import Path
import xml.etree.ElementTree as ET

import numpy as np

from intro_robotics.transforms import axis_rotation, rotx, roty, rotz, se3

URDF = Path(__file__).with_name("arm.urdf")


def read_numbers(element, name, default):
    """The numbers in an XML attribute such as xyz="0 0 0.2", or default if it is missing."""
    if element is None or element.get(name) is None:
        return np.array(default, dtype=float)
    numbers = []
    for word in element.get(name).split():
        numbers.append(float(word))
    return np.array(numbers)


def origin_transform(joint):
    """URDF origin: translate by xyz, rotate by Rz(yaw) @ Ry(pitch) @ Rx(roll)."""
    origin = joint.find("origin")
    xyz = read_numbers(origin, "xyz", [0, 0, 0])
    rpy = read_numbers(origin, "rpy", [0, 0, 0])
    roll = rpy[0]
    pitch = rpy[1]
    yaw = rpy[2]
    return se3(rotz(yaw) @ roty(pitch) @ rotx(roll), xyz)


def motion_transform(joint, value):
    """Rotation about (revolute) or translation along (prismatic) the axis."""
    kind = joint.get("type")
    if kind == "fixed":
        return np.eye(4)
    axis = read_numbers(joint.find("axis"), "xyz", [1, 0, 0])
    axis = axis / np.linalg.norm(axis)
    if kind == "prismatic":
        return se3(translation=value * axis)
    if kind not in ["revolute", "continuous"]:
        raise ValueError(f"Unsupported joint type {kind} in {joint.get('name')}")
    return se3(axis_rotation(axis, value))


def link_pose(link, positions, root="world", path=URDF):
    """Return T_root_link for joint positions given as {joint name: value}.

    Raises KeyError naming the link where the chain back to root breaks.
    """
    robot = ET.parse(path).getroot()
    parent_joint = {}  # for each link, the joint that moves it
    for joint in robot.findall("joint"):
        child = joint.find("child").get("link")
        parent_joint[child] = joint
    transform = np.eye(4)
    while link != root:
        joint = parent_joint[link]  # KeyError: no joint leads to this link
        value = positions.get(joint.get("name"), 0.0)
        transform = origin_transform(joint) @ motion_transform(joint, value) @ transform
        link = joint.find("parent").get("link")
    return transform
