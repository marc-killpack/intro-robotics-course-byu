"""The student-facing contract: what a controller receives and returns.

Every control period (default 0.02 s) the runner calls controller.step(obs)
with an Observation and expects a Command. The command takes effect one
period later, held constant for one period, exactly as it would over ROS.
Object positions, labels, and velocities are never in Observation or Task;
estimate them from the images.
"""

from dataclasses import dataclass

import numpy as np

REQUESTS = ("hold", "pick", "release")
PHASES = ("idle", "lowering", "lifting", "holding", "releasing")

# @dataclass writes __init__ for Observation, Command, and Task. Each
# `name: type` line just lists one field and what it holds (the one place the
# course writes type annotations); a field with "= value" has that default.


@dataclass
class Observation:
    """One control period's measurements, stamped in simulated time."""

    time: float  # simulated seconds when the images and joint state were taken
    fixed_image: np.ndarray  # (H, W, 3) uint8 RGB from the fixed overview camera
    tool_image: np.ndarray  # (H, W, 3) uint8 RGB from the tool-mounted camera
    q: np.ndarray  # joint positions, radians
    dq: np.ndarray  # joint velocities, radians per second
    actuator: str  # pickup phase, one of PHASES


@dataclass
class Command:
    """Joint-velocity command and pickup request for the next period."""

    dq: np.ndarray  # joint velocities, radians per second
    request: str = "hold"  # pickup request, one of REQUESTS

    def __post_init__(self):
        # Runs right after __init__ stores the fields: check them early.
        self.dq = np.asarray(self.dq, dtype=float)
        if self.dq.ndim != 1 or not np.all(np.isfinite(self.dq)):
            raise ValueError("Command.dq must be a finite 1-D array of joint velocities")
        if self.request not in REQUESTS:
            raise ValueError(f"Command.request must be one of {REQUESTS}")


@dataclass
class Task:
    """Fixed, known information about the scenario (no object truth).

    arm: SerialArm with its world base placement (the arm plane is
        `arm_height` above the belt) and joint limits.
    fixed_camera: (width, height, focal) of the overview camera. Its pose is
        not given, and the graded evaluation moves it slightly: calibrate a
        belt-plane homography from calibration_image at the start of every run.
    calibration_image: (H, W, 3) uint8 RGB from the fixed camera of the
        stopped, empty belt with the checkerboard lying on it. The board is
        removed before the episode, so Observation images never show it.
    board: {"squares": (nx, ny), "square": side (m), "center": (x, y) world}.
        Its long side runs along the belt; see vision.board_corners.
    tool_camera: intrinsics and T_tool_camera, as a Camera with mount='tool'.
    bins: {name: (x, y, radius)} in world meters.
    rules: {(color, shape): bin name}.
    marks: world XY of small dark marks on the belt (HW08 and HW09 scenarios
        only; project scenarios use the board instead).
    """

    arm: object  # SerialArm
    arm_height: float  # arm plane above the belt, m
    speed_limit: float  # each joint, rad/s
    acceleration_limit: float  # each joint, rad/s^2
    control_period: float  # seconds between step() calls
    pickup: dict  # the scenario's [pickup] table (timing, pick radius and speed)
    belt: dict  # {"y", "width", "x_start", "x_end"} in meters
    bins: dict
    rules: dict
    fixed_camera: tuple
    tool_camera: object
    colors: dict = None  # color name -> nominal (r, g, b)
    calibration_image: np.ndarray = None  # project scenarios (with a [board] table)
    board: dict = None
    marks: np.ndarray = None  # HW08/HW09 scenarios (with a [marks] table)


class Controller:
    """Base class for project controllers. Subclass it and override step().

    The runner calls reset() once before an episode and step() every control
    period. Keep any memory (filters, the current target, a state machine)
    as attributes of your subclass.

    Optional RL hooks (only for the Gymnasium wrapper in skill_env.py): split
    step() into skill_features(obs), which updates your memory and returns a
    feature vector of length skill_size while the learned sub-skill is in
    charge (None otherwise), and skill_command(obs, action), which returns
    this period's Command; action is None when your own controller decides.
    Then step() is simply skill_features followed by skill_command(obs, None).
    """

    skill_size = 0  # length of skill_features vectors (RL hooks only)
    action_size = 0  # length of the action skill_command accepts

    def __init__(self, task):
        self.task = task

    def reset(self):
        """Clear per-episode memory. The default does nothing."""

    def step(self, obs):
        """Return a Command. The default holds the arm still."""
        return Command(np.zeros(self.task.arm.n))

    def skill_features(self, obs):
        """RL hook: a 1-D feature vector while the learned skill acts, else None."""
        return None

    def skill_command(self, obs, action=None):
        """RL hook: this period's Command. Without the hooks, it is step(obs)."""
        return self.step(obs)
