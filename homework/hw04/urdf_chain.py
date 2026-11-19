"""Provided offline URDF reader for HW04 problem 5 (no ROS needed).

It follows the joints from one link back to the root, the way ROS's
robot_state_publisher builds TF: each joint contributes its fixed origin
(xyz, then roll-pitch-yaw) followed by its motion about its axis. The public
check uses it to compare your URDF with your SerialArm.fk.
"""

from pathlib import Path
import xml.etree.ElementTree as ET

import numpy as np

from intro_robotics.transforms import rotx, roty, rotz, se3

URDF = Path(__file__).with_name("arm.urdf")


def _numbers(element, name, default):
    text = element.get(name) if element is not None else None
    return np.array([float(v) for v in text.split()]) if text else np.array(default, float)


def origin_transform(joint):
    """URDF origin: translate by xyz, rotate by Rz(yaw) @ Ry(pitch) @ Rx(roll)."""
    origin = joint.find("origin")
    xyz = _numbers(origin, "xyz", [0, 0, 0])
    roll, pitch, yaw = _numbers(origin, "rpy", [0, 0, 0])
    return se3(rotz(yaw) @ roty(pitch) @ rotx(roll), xyz)


def motion_transform(joint, value):
    """Rotation about (revolute) or translation along (prismatic) the axis."""
    kind = joint.get("type")
    if kind == "fixed":
        return np.eye(4)
    axis = _numbers(joint.find("axis"), "xyz", [1, 0, 0])
    axis = axis / np.linalg.norm(axis)
    if kind == "prismatic":
        return se3(translation=value * axis)
    if kind not in ("revolute", "continuous"):
        raise ValueError(f"Unsupported joint type {kind!r} in {joint.get('name')}")
    skew = np.array([[0, -axis[2], axis[1]], [axis[2], 0, -axis[0]], [-axis[1], axis[0], 0]])
    rotation = np.eye(3) + np.sin(value) * skew + (1 - np.cos(value)) * skew @ skew
    return se3(rotation)


def link_pose(link, positions, root="world", path=URDF):
    """Return T_root_link for joint positions given as {joint name: value}.

    Raises KeyError naming the link where the chain back to root breaks.
    """
    robot = ET.parse(path).getroot()
    parent_joint = {j.find("child").get("link"): j for j in robot.findall("joint")}
    transform = np.eye(4)
    while link != root:
        joint = parent_joint[link]  # KeyError: no joint leads to this link
        value = positions.get(joint.get("name"), 0.0)
        transform = origin_transform(joint) @ motion_transform(joint, value) @ transform
        link = joint.find("parent").get("link")
    return transform
