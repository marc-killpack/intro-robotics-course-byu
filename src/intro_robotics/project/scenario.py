"""Read a scenario file (TOML) and build the arm, cameras, and Task from it.

Scenario files live in homework/project/scenarios/. A name such as "s1"
finds the file whose name starts with it there. Image size, rates, noise,
and belt-speed variation are all scenario settings.

The [realism] table is a switch (decision D1(g)): develop with it off, turn
it on when the pipeline works; graded scenarios have it on. When it is on,
its image_noise and speed_variation are copied into [cameras] and [belt];
when it is off, both are zero. A file may start from another with
`base = "name.toml"` and change only some tables (the faculty held-out
evaluation does this).
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


def find_scenario(name_or_path, folder=SCENARIO_DIR):
    """Path of a scenario file, from a path or a short name like 's1'."""
    path = Path(name_or_path)
    if path.exists():
        return path
    if (Path(folder) / path).exists():
        return Path(folder) / path
    matches = sorted(Path(folder).glob(f"{name_or_path}*.toml"))
    if len(matches) != 1:
        raise FileNotFoundError(f"No single scenario matches {name_or_path!r} in {folder}")
    return matches[0]


def merge(base, changes):
    """Copy of base with changes applied; tables merge, other values replace."""
    merged = dict(base)
    for key, value in changes.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def read_scenario(path):
    with Path(path).open("rb") as file:
        scenario = tomllib.load(file)
    if "base" in scenario:
        name = scenario.pop("base")
        try:  # next to this file first, then the student scenario folder
            base_path = find_scenario(name, Path(path).parent)
        except FileNotFoundError:
            base_path = find_scenario(name)
        if base_path.resolve() == Path(path).resolve():
            raise ValueError(f"{path} names itself as its base")
        scenario = merge(read_scenario(base_path), scenario)
    return scenario


def set_realism(scenario, enabled=None):
    """Apply the [realism] switch; enabled=None keeps the file's setting."""
    realism = scenario.get("realism")
    if realism is None:
        return scenario
    if enabled is not None:
        realism["enabled"] = bool(enabled)
    on = realism.get("enabled", False)
    scenario["cameras"]["image_noise"] = realism["image_noise"] if on else 0.0
    scenario["belt"]["speed_variation"] = realism["speed_variation"] if on else 0.0
    return scenario


def load_scenario(name_or_path, realism=None):
    """Return the scenario as a dict, from a path or a short name like 's1'.

    realism: None uses the file's [realism] enabled setting; True or False
    overrides it (image noise and belt-speed variation on or off).
    """
    path = find_scenario(name_or_path)
    scenario = read_scenario(path)
    scenario["path"] = str(path)
    return set_realism(scenario, realism)


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


def board(scenario):
    """The [board] table as task.board, or None."""
    if "board" not in scenario:
        return None
    b = scenario["board"]
    return {"squares": tuple(int(n) for n in b["squares"]), "square": float(b["square"]),
            "center": tuple(float(c) for c in b["center"])}


def make_task(scenario):
    """The information a student controller is allowed to know."""
    from .simulator import calibration_image  # the simulator imports this module

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
        tool_camera=tool,
        colors={k: tuple(v) for k, v in scenario["colors"].items()},
        calibration_image=calibration_image(scenario) if "board" in scenario else None,
        board=board(scenario),
        marks=np.array(scenario["marks"]["xy"], float) if "marks" in scenario else None,
    )
