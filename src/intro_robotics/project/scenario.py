"""Read a scenario file (TOML) and build the arm, cameras, and Task from it.

Scenario files live in homework/project/scenarios/. A name such as "s1"
finds the file whose name starts with it there. Image size, rates, noise,
and belt-speed variation are all scenario settings.
"""

from pathlib import Path
import tomllib

import numpy as np

from ..camera import Camera
from ..kinematics import Joint, SerialArm
from .contract import Task


def pose(rotation=None, translation=None):
    """4x4 transform from a rotation and translation (written out directly so
    the supplied simulator never depends on the student's se3)."""
    transform = np.eye(4)
    if rotation is not None:
        transform[:3, :3] = rotation
    if translation is not None:
        transform[:3, 3] = translation
    return transform


SCENARIO_DIR = Path(__file__).resolve().parents[3] / "homework" / "project" / "scenarios"


def load_scenario(name_or_path):
    """Return the scenario as a dict, from a path or a short name like 's1'."""
    path = Path(name_or_path)
    if not path.exists():
        matches = sorted(SCENARIO_DIR.glob(f"{name_or_path}*.toml"))
        if len(matches) != 1:
            raise FileNotFoundError(f"No single scenario matches {name_or_path!r} in {SCENARIO_DIR}")
        path = matches[0]
    with path.open("rb") as file:
        scenario = tomllib.load(file)
    scenario["path"] = str(path)
    return scenario


def make_arm(scenario):
    """Planar revolute arm; its plane is arm.height above the belt (z = 0)."""
    arm = scenario["arm"]
    joints = [
        Joint("z", tip=pose(translation=[length, 0, 0]), limits=tuple(limits))
        for length, limits in zip(arm["link_lengths"], arm["joint_limits"])
    ]
    return SerialArm(joints, base=pose(translation=[*arm["base_xy"], arm["height"]]))


def look_at(location, target):
    """T_world_camera for a camera at location looking at target (image x = world x)."""
    location = np.asarray(location, float)
    forward = np.asarray(target, float) - location
    forward /= np.linalg.norm(forward)
    right = np.array([1.0, 0, 0])
    right -= forward * (right @ forward)
    right /= np.linalg.norm(right)
    down = np.cross(forward, right)
    return pose(np.column_stack((right, down, forward)), location)


def make_cameras(scenario):
    """Return (fixed Camera, tool Camera) built from the [cameras] table."""
    c = scenario["cameras"]
    fixed = Camera(
        look_at(c["fixed_location"], c["fixed_target"]),
        width=c["width"], height=c["height"], focal=c["fixed_focal"],
    )
    # Straight down from the tool: camera x = tool x, camera z = -tool z.
    tool = Camera(
        pose(np.diag([1.0, -1.0, -1.0]), c["tool_offset"]),
        mount="tool", width=c["width"], height=c["height"], focal=c["tool_focal"],
    )
    return fixed, tool


def make_task(scenario):
    """The information a student controller is allowed to know."""
    arm = make_arm(scenario)
    fixed, tool = make_cameras(scenario)
    rules = {tuple(key.split()): value for key, value in scenario["rules"].items()}
    return Task(
        arm=arm,
        arm_height=scenario["arm"]["height"],
        speed_limit=scenario["arm"]["speed_limit"],
        acceleration_limit=scenario["arm"]["acceleration_limit"],
        control_period=scenario["control_period"],
        pickup=dict(scenario["pickup"]),
        belt={k: scenario["belt"][k] for k in ("y", "width", "x_start", "x_end")},
        bins={name: tuple(v) for name, v in scenario["bins"].items()},
        rules=rules,
        fixed_camera=(fixed.width, fixed.height, fixed.focal),
        marks=np.array(scenario["marks"]["xy"], float),
        tool_camera=tool,
        colors={k: tuple(v) for k, v in scenario["colors"].items()},
    )
