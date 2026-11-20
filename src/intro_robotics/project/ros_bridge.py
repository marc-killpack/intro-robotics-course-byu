"""Supplied helpers shared by the project's ROS nodes (no ROS import here).

The live graph (sim_node.py, controller_node.py) needs a URDF for the
scenario's arm, image and camera-info fields, scene markers, and names. They
are plain Python so they can be checked without ROS.

Frames (all meters, world Z up, belt surface at z = 0):

    world -> arm_base (base_xy, arm height) -> arm_link1 ... arm_link4
          -> tool_flange (end of link 4, in the arm plane)
          -> tool (pickup_joint: a prismatic stroke straight down)
          -> tool_camera_optical (moves with the tool, as in the simulator)
    world -> fixed_camera_optical

Camera frames use the ROS optical convention (x right, y down, z forward),
which is also the course Camera convention.
"""

import math

import numpy as np

from .scenario import make_cameras

ARM_JOINT_PREFIX = "joint"
PICKUP_JOINT = "pickup_joint"
FIXED_CAMERA_FRAME = "fixed_camera_optical"
TOOL_CAMERA_FRAME = "tool_camera_optical"


def arm_joint_names(n):
    return [f"{ARM_JOINT_PREFIX}{i + 1}" for i in range(n)]


def rpy_from_rotation(rotation):
    """URDF roll-pitch-yaw angles with R = Rz(yaw) @ Ry(pitch) @ Rx(roll)."""
    r = np.asarray(rotation, float)
    pitch = math.asin(max(-1.0, min(1.0, -r[2, 0])))
    if abs(math.cos(pitch)) > 1e-9:
        roll = math.atan2(r[2, 1], r[2, 2])
        yaw = math.atan2(r[1, 0], r[0, 0])
    else:  # gimbal lock: put all of the remaining rotation in yaw
        roll = 0.0
        yaw = math.atan2(-r[0, 1], r[1, 1])
    return roll, pitch, yaw


def _origin(xyz=(0, 0, 0), rpy=(0, 0, 0)):
    return 'xyz="{:.12g} {:.12g} {:.12g}" rpy="{:.12g} {:.12g} {:.12g}"'.format(*xyz, *rpy)


def arm_urdf(scenario):
    """URDF text for the scenario's planar arm, pickup stroke, and cameras."""
    a = scenario["arm"]
    lengths = a["link_lengths"]
    height = a["height"]
    fixed_camera, tool_camera = make_cameras(scenario)
    names = arm_joint_names(len(lengths))
    radius = a["link_radius"]
    parts = [
        '<?xml version="1.0"?>',
        "<!-- Generated from the scenario file by intro_robotics.project.ros_bridge. -->",
        f'<robot name="conveyor_arm">',
        '  <material name="grey"><color rgba="0.55 0.55 0.55 1"/></material>',
        '  <material name="blue"><color rgba="0.2 0.4 0.8 1"/></material>',
        '  <material name="orange"><color rgba="0.95 0.5 0.1 1"/></material>',
        '  <material name="black"><color rgba="0.1 0.1 0.1 1"/></material>',
        '  <link name="world"/>',
        # A pedestal from the belt surface up to the arm plane.
        '  <link name="arm_base"><visual>'
        f'<origin {_origin((0, 0, -height / 2))}/>'
        f'<geometry><cylinder radius="0.05" length="{height:.6g}"/></geometry>'
        '<material name="grey"/></visual></link>',
        '  <joint name="world_joint" type="fixed"><parent link="world"/><child link="arm_base"/>'
        f'<origin {_origin((*a["base_xy"], height))}/></joint>',
    ]
    parent, offset = "arm_base", 0.0
    for i, (name, length, (low, high)) in enumerate(zip(names, lengths, a["joint_limits"])):
        link = f"arm_link{i + 1}"
        parts += [
            f'  <link name="{link}"><visual>'
            f'<origin {_origin((length / 2, 0, 0), (0, math.pi / 2, 0))}/>'
            f'<geometry><cylinder radius="{radius:.6g}" length="{length:.6g}"/></geometry>'
            '<material name="blue"/></visual></link>',
            f'  <joint name="{name}" type="revolute"><parent link="{parent}"/><child link="{link}"/>'
            f'<origin {_origin((offset, 0, 0))}/><axis xyz="0 0 1"/>'
            f'<limit lower="{low:.6g}" upper="{high:.6g}" effort="1" velocity="{a["speed_limit"]:.6g}"/></joint>',
        ]
        parent, offset = link, length
    camera_rpy = rpy_from_rotation(tool_camera.transform[:3, :3])
    parts += [
        '  <link name="tool_flange"/>',
        f'  <joint name="flange_joint" type="fixed"><parent link="{parent}"/><child link="tool_flange"/>'
        f'<origin {_origin((offset, 0, 0))}/></joint>',
        # The pickup stroke: the tool slides straight down from the arm plane.
        '  <link name="tool"><visual><origin xyz="0 0 0.05"/>'
        '<geometry><cylinder radius="0.008" length="0.1"/></geometry><material name="orange"/></visual>'
        '<visual><geometry><sphere radius="0.015"/></geometry><material name="orange"/></visual></link>',
        f'  <joint name="{PICKUP_JOINT}" type="prismatic"><parent link="tool_flange"/><child link="tool"/>'
        f'<axis xyz="0 0 -1"/><limit lower="0" upper="{height:.6g}" effort="1" velocity="1"/></joint>',
        f'  <link name="{TOOL_CAMERA_FRAME}"><visual><origin xyz="0 0 -0.01"/>'
        '<geometry><box size="0.03 0.03 0.02"/></geometry><material name="black"/></visual></link>',
        f'  <joint name="tool_camera_joint" type="fixed"><parent link="tool"/><child link="{TOOL_CAMERA_FRAME}"/>'
        f'<origin {_origin(tool_camera.transform[:3, 3], camera_rpy)}/></joint>',
        f'  <link name="{FIXED_CAMERA_FRAME}"><visual><origin xyz="0 0 -0.02"/>'
        '<geometry><box size="0.06 0.04 0.04"/></geometry><material name="black"/></visual></link>',
        f'  <joint name="fixed_camera_joint" type="fixed"><parent link="world"/><child link="{FIXED_CAMERA_FRAME}"/>'
        f'<origin {_origin(fixed_camera.transform[:3, 3], rpy_from_rotation(fixed_camera.transform[:3, :3]))}/></joint>',
        "</robot>",
    ]
    return "\n".join(parts) + "\n"


def stroke(simulator):
    """How far the tool has moved down from the arm plane (pickup_joint, m)."""
    return simulator.height - simulator.tool_pose()[2, 3]


def joint_state_fields(simulator):
    """(names, positions, velocities) for the JointState message."""
    names = arm_joint_names(simulator.n) + [PICKUP_JOINT]
    return names, [*map(float, simulator.q), stroke(simulator)], [*map(float, simulator.dq), 0.0]


def arm_state_from_fields(names, positions, velocities, n):
    """Arm joint positions and velocities, in joint order, from JointState fields."""
    index = {name: i for i, name in enumerate(names)}
    order = [index[name] for name in arm_joint_names(n)]  # KeyError if a joint is missing
    velocities = list(velocities) if len(velocities) else [0.0] * len(names)
    return np.array([positions[i] for i in order]), np.array([velocities[i] for i in order])


def camera_info_fields(camera):
    """width, height, and the K and P matrices for sensor_msgs/CameraInfo.

    The course Camera puts pixel centers at u + 0.5; ROS puts them at integer
    u, so the principal point moves half a pixel.
    """
    cx, cy = camera.width / 2 - 0.5, camera.height / 2 - 0.5
    f = float(camera.focal)
    k = [f, 0.0, cx, 0.0, f, cy, 0.0, 0.0, 1.0]
    p = [f, 0.0, cx, 0.0, 0.0, f, cy, 0.0, 0.0, 0.0, 1.0, 0.0]
    return camera.width, camera.height, k, p


def image_from_fields(height, width, encoding, data):
    """NumPy RGB image from sensor_msgs/Image fields (no cv_bridge needed)."""
    if encoding != "rgb8":
        raise ValueError(f"Expected an rgb8 image, got {encoding!r}")
    return np.frombuffer(bytes(data), dtype=np.uint8).reshape(height, width, 3)


# Marker shapes; the values match visualization_msgs/Marker constants.
CUBE, CYLINDER, TRIANGLE_LIST = 1, 3, 11


def scene_markers(scenario):
    """Known scene geometry (no object truth) as plain marker descriptions.

    Each entry is a dict with type, position, scale, color (0-1 RGBA), and an
    optional list of points. The sim node turns them into a MarkerArray.
    """
    belt = scenario["belt"]
    grey = [c / 255 for c in (150, 150, 150)] + [1.0]
    markers = [dict(type=CUBE, position=[(belt["x_start"] + belt["x_end"]) / 2, belt["y"], -0.003],
                    scale=[belt["x_end"] - belt["x_start"], belt["width"], 0.006], color=grey)]
    for x, y, r in scenario["bins"].values():
        markers.append(dict(type=CYLINDER, position=[x, y, 0.01], scale=[2 * r, 2 * r, 0.02],
                            color=[0.35, 0.35, 0.35, 1.0]))
    size = scenario["marks"]["size"]
    for x, y in scenario["marks"]["xy"]:
        markers.append(dict(type=CUBE, position=[x, y, 0.001], scale=[size, size, 0.002],
                            color=[0.06, 0.06, 0.06, 1.0]))
    return markers


def object_markers(simulator):
    """Faculty truth for a demonstration view: objects on the belt and held.

    Never publish these on a topic a student controller reads.
    """
    markers = []
    for obj in simulator.objects:
        if not (simulator.on_belt(obj) or obj.state == "held"):
            continue
        z = simulator.tool_pose()[2, 3] if obj.state == "held" else 0.0
        color = [c / 255 for c in simulator.scenario["colors"][obj.color]] + [1.0]
        if obj.shape == "triangle":
            corners = obj.outline() - obj.position
            markers.append(dict(type=TRIANGLE_LIST, position=[*obj.position, z + 0.004],
                                scale=[1.0, 1.0, 1.0], color=color,
                                points=[[x, y, 0.0] for x, y in corners]))
        elif obj.shape == "square":
            side = 0.85 * obj.size
            markers.append(dict(type=CUBE, position=[*obj.position, z + 0.004], yaw=obj.yaw + math.pi / 4,
                                scale=[side, side, 0.008], color=color))
        else:
            markers.append(dict(type=CYLINDER, position=[*obj.position, z + 0.004],
                                scale=[obj.size, obj.size, 0.008], color=color))
    return markers


if __name__ == "__main__":
    # The launch file runs this to get the URDF: python3 -m intro_robotics.project.ros_bridge s2
    import sys

    from .scenario import load_scenario

    print(arm_urdf(load_scenario(sys.argv[1] if len(sys.argv) > 1 else "s1")), end="")
