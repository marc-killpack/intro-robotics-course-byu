"""Generate the course map poster for students (faculty-maintained).

One source of truth for two outputs, both written next to this file:

    robot_stack.svg   static poster for slides, handouts, and the README
    robot_stack.html  interactive page: click an idea, tool, or part of the
                      robot to light up how it connects to the others

Run from the repository root after editing the content below:

    python docs/figures/robot_stack.py

The poster has three rows. The ideas (course outcomes 2-9) are on top. Each
idea is built with tools in the middle row, and each tool works with a piece
of the robot in the illustrated conveyor cell at the bottom. The cell is
simulated in this course; on a real robot the same controller code runs.
"""

import html
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
WIDTH = 1240

# ---------------------------------------------------------------------------
# Content. Keep facts matched to the homework and project files.
# ---------------------------------------------------------------------------

METHOD_ORDER = ["frames", "kin", "vel", "plan", "vision", "servo", "classify", "rl"]
METHODS = {
    "frames": {
        "title": "Frames", "sub": "rotations, transforms", "outcome": 2, "hw": "HW02–03",
        "tools": ["ros", "numpy"],
        "what": "Describe where things are, and convert between what the camera sees, the belt, and the robot.",
        "learn": ["HW02 rotations", "HW03 transforms and TF"],
        "project": "Map a detected part from the camera's view into the robot's base frame, and place the wrist camera with T_world_tool @ T_tool_camera.",
        "real": "Every sensor has a frame. A hand-eye calibration finds where a camera sits on the robot, and TF keeps all the frames straight.",
    },
    "kin": {
        "title": "Kinematics", "sub": "forward and inverse", "outcome": 3, "hw": "HW04, HW06",
        "tools": ["ros", "numpy"],
        "what": "Go from joint angles to where the tool is (forward), and from a target back to joint angles (inverse).",
        "learn": ["HW04 forward kinematics and URDF", "HW06 inverse kinematics"],
        "project": "Forward kinematics places the suction cup and the wrist camera; damped pseudo-inverse IK turns a target position into joint angles.",
        "real": "Robot controllers and MoveIt 2 compute FK and IK from the robot's URDF, the same math you write.",
    },
    "vel": {
        "title": "Velocity", "sub": "Jacobians, twists", "outcome": 4, "hw": "HW05–06",
        "tools": ["numpy"],
        "what": "Relate joint speeds to how fast the tool moves (the Jacobian), and run it backward to steer the tool.",
        "learn": ["HW05 planar Jacobians", "HW06 damped least squares", "HW09 the image Jacobian"],
        "project": "Damped least squares turns the tool velocity you want into the joint velocities your controller sends.",
        "real": "Jogging a robot in a straight line and steering clear of singular poses both use the Jacobian.",
    },
    "plan": {
        "title": "Path planning", "sub": "RRT, trajectories", "outcome": 5, "hw": "HW06–07",
        "tools": ["ros", "numpy", "scipy"],
        "what": "Find a path that avoids obstacles, and turn it into a smooth motion over time.",
        "learn": ["HW06 RRT-Connect in configuration space", "HW07 trajectories", "Lecture P6 optimization"],
        "project": "Choosing which part to go after, and when, is a planning decision; the second round adds obstacles to plan around.",
        "real": "Motion planners such as those in MoveIt 2 plan around obstacles in the robot's workspace before it moves.",
    },
    "vision": {
        "title": "Computer vision", "sub": "find and track parts", "outcome": 6, "hw": "HW08",
        "tools": ["opencv"],
        "what": "Turn pixels into parts: where each one is on the belt, its color and shape, and how fast it moves.",
        "learn": ["HW08 homography, color and shape, tracking", "Project launch: checkerboard calibration"],
        "project": "Calibrate the overhead camera from the checkerboard, then detect, classify, and track every part on the belt.",
        "real": "Inspection lines and bin-picking cells find and sort parts from camera images.",
    },
    "servo": {
        "title": "Visual servoing", "sub": "steer with a camera", "outcome": 7, "hw": "HW09",
        "tools": ["numpy", "opencv"],
        "what": "Close the loop with a camera: move until the target appears where you want it in the image.",
        "learn": ["HW09 image-based visual servoing"],
        "project": "The final approach: move the arm until the wrist camera sees the part at the target pixel, then pick.",
        "real": "Visual servoing absorbs small calibration errors, so the gripper lands where the camera says the part is.",
    },
    "classify": {
        "title": "Classification", "sub": "learn from examples", "outcome": 8, "hw": "HW10",
        "tools": ["torch"],
        "what": "Train a network to recognize parts from labeled examples when hand-written rules break.",
        "learn": ["HW10 a small image classifier"],
        "project": "Optional: classify parts with your network instead of the HW08 rules. On hard lighting it scored about 97% where the rules scored 40%.",
        "real": "Factories train networks to spot defects and sort parts when lighting and clutter vary.",
    },
    "rl": {
        "title": "Reinforcement", "sub": "learning from reward", "outcome": 9, "hw": "HW11",
        "tools": ["torch", "gym"],
        "what": "Learn a behavior by trial and error from a reward, in simulation.",
        "learn": ["HW11 reward shaping for interception", "RL lectures in weeks 11–12"],
        "project": "Optional: learn a correction to one skill, such as the visual-servoing approach, in the project's SkillEnv.",
        "real": "Policies trained in simulation now run walking robots and robot hands; randomizing the simulation helps them transfer.",
    },
}

TOOL_ORDER = ["docker", "ros", "mpl", "plotjuggler", "numpy", "scipy", "opencv", "torch", "gym"]

# Dotted lines: tools that run, show, or carry an idea's work without being
# what the idea is built from. ROS 2: the project carries images and
# velocity commands on topics. Docker runs every idea from HW06 on; its eight
# lines crowded the poster, so its card says so instead.
USED_WITH = {
    "ros": ["vel", "vision", "servo"],
    "mpl": ["frames", "kin", "vel", "plan", "vision", "servo", "classify"],
    "plotjuggler": ["vel", "plan"],
}
TOOLS = {
    "docker": {
        "name": "Docker", "tag": "same setup anywhere", "used": "HW01, all from HW06",
        "parts": ["computer"],
        "what": "Packages Ubuntu, ROS 2, and every library into one image that runs the same on any computer.",
        "learn": ["HW01 setup", "HW03–HW04 ROS problems", "All work from HW06"],
        "project": "The whole project, every ROS 2 node included, runs in the course container.",
        "real": "Teams ship the same image to the robot's computer, so what worked on a laptop runs on the robot.",
        "reach": ["Making robot software run the same on a teammate's laptop and on the robot"],
        "beyond": ["Dev containers", "Deploying containers to fleets of robots"],
    },
    "ros": {
        "name": "ROS 2 + RViz", "tag": "nodes, frames, 3D", "used": "HW01–07, project",
        "parts": ["computer", "arm", "toolcam", "fixedcam", "cable"],
        "what": "ROS 2 lets separate programs (nodes) share messages on named topics. A URDF describes the robot, TF tracks its frames, and RViz draws it all in 3D.",
        "learn": ["HW01 joint states and RViz", "HW03 TF broadcaster", "HW04 your URDF against your fk()", "HW07 publish and subscribe", "Project node graph"],
        "project": "The cameras, the simulator, and your controller are separate nodes. Images come in on topics and joint velocity commands go out. RViz shows the arm and both camera images during a live run.",
        "real": "The same graph. Camera driver nodes and ros2_control replace the simulator, and ros2_control's joint-group velocity controller takes the same Float64MultiArray command.",
        "reach": ["Splitting robot software into parts that run and restart separately", "Checking that frames and the robot model match what you see", "Expressing a point the camera sees in the robot's base frame"],
        "beyond": ["ros2_control for hardware", "MoveIt 2 for arms, Nav2 for mobile robots", "rosbag2 to record tests"],
    },
    "mpl": {
        "name": "Matplotlib", "tag": "plot your results", "used": "HW02–10, project",
        "parts": ["computer"],
        "what": "Plots and figures from Python.",
        "learn": ["HW02–HW10 activities (--show, --save)", "HW10 confusion matrix", "Project run.py figures"],
        "project": "Save camera frames and run results, and plot score and failures across seeds for your report.",
        "real": "The same: analyze logged runs after a test.",
        "reach": ["Comparing results over many seeded runs", "Plotting calibration error across the belt", "Making figures for a report"],
        "beyond": ["Jupyter notebooks for experiment analysis", "pandas for large logs"],
    },
    "plotjuggler": {
        "name": "PlotJuggler", "tag": "plot live signals", "used": "HW01, HW07, project",
        "parts": ["arm"],
        "what": "Live and recorded time plots of any ROS 2 topic.",
        "learn": ["HW01 problem 4(e): a joint angle over time", "Planned: HW07 trajectory velocity", "Planned: project session 11.2"],
        "project": "Plot commanded against measured joint velocity to see saturation and delay while you tune gains.",
        "real": "The same tool, reading the motors' encoders. It also opens recorded rosbag2 (MCAP) files after a test.",
        "reach": ["Tuning a controller gain", "Spotting a glitch or a dropped message in a sensor stream", "Checking that a trajectory is smooth"],
        "beyond": ["rosbag2 to record every topic during a test", "Foxglove for plots and video together"],
    },
    "numpy": {
        "name": "NumPy", "tag": "math on arrays", "used": "HW02 → project",
        "parts": ["arm"],
        "what": "Arrays and linear algebra in Python. Almost every idea in the course is written in it.",
        "learn": ["HW02 rotation matrices", "HW03 transforms", "HW04 FK", "HW05 Jacobian", "HW06 IK and RRT", "HW09 IBVS"],
        "project": "Your controller does its math in NumPy: frame transforms, FK, the Jacobian, the damped least-squares solve, and the servoing law that turns image features into joint velocities.",
        "real": "Unchanged. The same code runs on the robot's computer; only the source of images and joint angles changes.",
        "reach": ["Computing where the suction cup is from joint angles", "Finding joint speeds that move the tool toward a target", "Checking a calibration with a held-out point"],
        "beyond": ["Kinematics libraries (Pinocchio, KDL) that read a URDF", "Drake for optimization and control"],
    },
    "scipy": {
        "name": "SciPy", "tag": "optimize, solve", "used": "lecture P6",
        "parts": ["arm"],
        "what": "Scientific Python: optimization, linear algebra, and signal processing.",
        "learn": ["Lecture P6: position-only optimization with joint-limit constraints"],
        "project": "Optional: optimize a path or an interception time with joint limits as constraints.",
        "real": "The same code; solvers often run online at a fixed rate on the robot.",
        "reach": ["Solving an optimization with constraints such as joint limits", "Filtering a noisy signal"],
        "beyond": ["Trajectory optimization (Drake, CasADi)", "Optimization-based planners in MoveIt 2"],
    },
    "opencv": {
        "name": "OpenCV", "tag": "see in images", "used": "HW08 → project",
        "parts": ["toolcam", "fixedcam"],
        "what": "The standard library for image processing and camera geometry.",
        "learn": ["HW08 plane homography, color masks, shapes, tracking", "Project launch: checkerboard corners for calibration"],
        "project": "Calibrate the overhead camera from the checkerboard, find and classify every part by color and shape, and track it to estimate the belt speed. The wrist camera's image drives your visual-servoing approach.",
        "real": "The same functions, but real images add lens distortion, glare, and lighting changes, so you also calibrate the lens itself (cv2.calibrateCamera).",
        "reach": ["Finding a part's pixel location", "Mapping pixels to belt coordinates", "Locating a part with a fiducial marker (ArUco, AprilTag)"],
        "beyond": ["Camera driver nodes (usb_cam, realsense2_camera) and cv_bridge", "Learned detectors such as YOLO when rules break"],
    },
    "torch": {
        "name": "PyTorch", "tag": "learn from data", "used": "HW10 → project",
        "parts": ["fixedcam"],
        "what": "A library for building and training neural networks.",
        "learn": ["HW10 the training loop and a small image classifier", "HW11 underneath Stable-Baselines3"],
        "project": "Optional: replace the HW08 rule classifier with your network on the overhead camera's view.",
        "real": "Train on a desktop GPU, then run the trained network on the robot's computer, often exported to ONNX or TensorRT to run faster.",
        "reach": ["Hand-written rules fail under lighting, blur, or clutter", "You have labeled examples of what the robot must recognize"],
        "beyond": ["Pretrained vision models (torchvision)", "Imitation learning and vision-language-action models (extension lectures)"],
    },
    "gym": {
        "name": "Gymnasium + SB3", "tag": "learn by trial", "used": "HW11 → project",
        "parts": ["arm"],
        "what": "Gymnasium defines an environment with reset() and step(); Stable-Baselines3 trains policies such as PPO on it.",
        "learn": ["HW11 reward shaping for interception", "RL lectures in weeks 11–12"],
        "project": "Optional: the project's SkillEnv wraps the same simulator. A learned correction to the servoing approach raised the held-out average from 136.7 to 144.",
        "real": "Train in simulation, then transfer. Randomizing the simulation (domain randomization) helps a policy survive the real robot's differences.",
        "reach": ["A behavior is easier to score than to program, such as timing an interception", "Fine-tuning a controller that already works"],
        "beyond": ["Isaac Lab and MuJoCo for fast parallel training", "Learned locomotion (extension lecture)"],
    },
}

PART_ORDER = ["computer", "arm", "toolcam", "fixedcam"]
PARTS = {
    "computer": {
        "num": 1, "name": "Computer", "x": 160, "sub": "runs every ROS 2 node",
        "simtext": "Your laptop runs every ROS 2 node in the course Docker image, and shows RViz and PlotJuggler.",
        "realtext": "The robot's computer runs the same image, often an embedded GPU board when networks run onboard.",
    },
    "arm": {
        "num": 2, "name": "Arm + suction cup", "x": 540, "sub": "4 joints, vacuum pickup",
        "simtext": "A planar 4-link arm (0.4, 0.3, 0.2, 0.2 m) with position, speed, and acceleration limits, and a suction pickup with a timed vertical stroke.",
        "realtext": "Servo motors with encoders and drives, and a vacuum cup on a vertical axis. Planar joints plus a vertical stroke is the layout of a SCARA robot, the usual conveyor pick-and-place arm.",
    },
    "toolcam": {
        "num": 3, "name": "Wrist camera", "x": 790, "sub": "moves with the tool",
        "simtext": "Rendered from T_world_tool @ T_tool_camera, so it moves with the arm.",
        "realtext": "A small camera on the wrist; its mounting pose comes from a hand-eye calibration.",
    },
    "fixedcam": {
        "num": 4, "name": "Overhead camera", "x": 1060, "sub": "watches the whole belt",
        "simtext": "A rendered 320 by 240 image of the belt, 50 times a second. Its pose changes in the graded run, so you calibrate it every run.",
        "realtext": "An overhead USB or industrial camera; calibrate its lens as well as the belt plane.",
    },
}
SCENERY = {
    "conveyor": {
        "name": "Conveyor and parts",
        "simtext": "A 0.06 m/s belt whose speed varies a little between episodes; parts in three colors and three shapes arrive about every 3.3 s, and you sort them into bins by a rule table.",
        "realtext": "A motor-driven belt. Industrial conveyor tracking adds a belt encoder to follow each part after the camera sees it.",
    },
    "cable": {
        "name": "ROS 2 topics",
        "simtext": "A topic is a named stream of messages; any node can publish or subscribe to it. Images come in on fixed_camera/image_raw and tool_camera/image_raw, your controller sends joint_velocity_command and actuator/request, and joint_states and actuator/state come back. The arrows in the picture show which way the messages flow.",
        "realtext": "The same topics, carried over Ethernet or USB from the camera drivers and the motor drives.",
    },
}

# Where each tool appears (interactive page only): 2 = used, 1 = optional or planned.
COLUMNS = ["HW01", "HW02", "HW03", "HW04", "HW05", "HW06", "HW07", "HW08", "HW09", "HW10", "HW11", "Project"]
WEEKS = ["W1", "W2", "W3", "W4", "W5", "W6", "W7", "W8", "W9", "W10", "W12", "W11-14"]
USAGE = {
    "docker": {c: 2 for c in ["HW01", "HW03", "HW04", "HW06", "HW07", "HW08", "HW09", "HW10", "HW11", "Project"]},
    "ros": {"HW01": 2, "HW03": 2, "HW04": 2, "HW07": 2, "Project": 2},
    "mpl": {c: 2 for c in ["HW02", "HW03", "HW04", "HW05", "HW06", "HW07", "HW08", "HW09", "HW10", "Project"]},
    "plotjuggler": {"HW01": 2, "HW07": 1, "Project": 1},
    "numpy": {c: 2 for c in COLUMNS[1:]},
    "scipy": {"HW07": 1},
    "opencv": {"HW08": 2, "HW09": 2, "Project": 2},
    "torch": {"HW10": 2, "HW11": 2, "Project": 1},
    "gym": {"HW11": 2, "Project": 1},
}
USAGE_NOTES = {
    ("plotjuggler", "HW07"): "planned", ("plotjuggler", "Project"): "planned",
    ("scipy", "HW07"): "lecture P6, same week", ("torch", "Project"): "optional",
    ("gym", "Project"): "optional",
}

# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------


def esc(value):
    return html.escape(str(value), quote=True)


def text(x, y, content, cls, anchor="middle"):
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{anchor}">{content}</text>'


def node_open(item_id, kind, label, focusable=True):
    keys = f' tabindex="0" role="button" aria-label="{esc(label)}"' if focusable else ""
    return f'<g class="node k-{kind}" data-id="{item_id}"{keys}>'


def curve(x1, y1, x2, y2):
    middle = (y1 + y2) / 2
    return f"M{x1:.1f},{y1:.1f} C{x1:.1f},{middle:.1f} {x2:.1f},{middle:.1f} {x2:.1f},{y2:.1f}"


def spread(center, count, step=13):
    """Anchor x positions for count edges leaving one side of a card."""
    return [center + (i - (count - 1) / 2) * step for i in range(count)]


# ---------------------------------------------------------------------------
# Pictograms, each drawn in a 48 by 48 box. Lines use the row's color
# (currentColor); the accent marks what the idea or tool is about.
# ---------------------------------------------------------------------------

STAR = "l2.4 5 5.5.7-4 3.8 1 5.4-4.9-2.6-4.9 2.6 1-5.4-4-3.8 5.5-.7z"
ICONS = {
    "frames": ('<path class="ic ax-x" d="M12 36H37"/><path class="ax-xf" d="M43 36l-7-4v8z"/>'
               '<path class="ic ax-z" d="M12 36V12"/><path class="ax-zf" d="M12 6l-4 7h8z"/>'
               '<path class="ic ax-y" d="M12 36L28 24"/><path class="ax-yf" d="M33 20l-2.7 6.4-4.2-5.6z"/>'
               '<circle cx="12" cy="36" r="3" class="ic-fill"/>'),
    "kin": ('<rect x="4" y="40" width="16" height="5" rx="1.5" class="ic-fill"/>'
            '<path class="ic" d="M12 40V30L26 17L38 25"/>'
            '<circle cx="12" cy="30" r="3.2" class="ic-dot"/><circle cx="26" cy="17" r="3.2" class="ic-dot"/>'
            '<circle cx="38" cy="25" r="7.5" class="ic-acc ic-dash"/><circle cx="38" cy="25" r="2.6" class="ic-fill"/>'),
    "vel": ('<rect x="4" y="40" width="16" height="5" rx="1.5" class="ic-fill"/>'
            '<path class="ic" d="M12 40V28L27 23"/>'
            '<circle cx="12" cy="28" r="3.2" class="ic-dot"/><circle cx="27" cy="23" r="3" class="ic-fill"/>'
            '<path class="ic-acc" d="M27 23L38 14"/><path class="ic-acc-fill" d="M44 9l-3.3 8.2-5-6z"/>'),
    "plan": ('<rect x="17" y="13" width="13" height="17" rx="2.5" class="ic-soft"/>'
             '<path class="ic ic-dash" d="M8 40C24 42 37 38 37 26S38 14 39 10"/>'
             '<circle cx="8" cy="40" r="3.6" class="ic-fill"/>'
             '<path class="ic-acc" d="M39 15V3"/><path class="ic-acc-fill" d="M39 3l8 3.2-8 3.2z"/>'),
    "vision": ('<rect x="4" y="7" width="40" height="31" rx="3.5" class="ic"/>'
               '<circle cx="17" cy="25" r="5" class="sh-red"/><path d="M32 14l6 10.5H26z" class="sh-yellow"/>'
               '<path class="ic-acc" d="M10 21v-3h3 M21 18h3v3 M24 29v3h-3 M13 32h-3v-3"/>'
               '<path class="ic" d="M24 38v5 M16 44h16"/>'),
    "servo": ('<circle cx="24" cy="24" r="16" class="ic"/>'
              '<path class="ic" d="M24 3v9 M24 36v9 M3 24h9 M36 24h9"/>'
              '<circle cx="24" cy="24" r="3" class="ic-acc"/>'
              '<circle cx="32" cy="16" r="4.2" class="sh-red"/>'
              '<path class="ic-acc" d="M29 19l-2.5 2.5"/>'),
    "classify": ('<circle cx="9" cy="9" r="5" class="sh-red"/><rect x="19" y="4" width="10" height="10" class="sh-blue"/>'
                 '<path d="M39 3.5l6 11H33z" class="sh-yellow"/>'
                 '<path class="ic-acc" d="M9 18l4 9 M24 18v9 M39 18l-4 9"/>'
                 '<path class="ic" d="M5 30v12h16V30 M27 30v12h16V30"/>'),
    "rl": ('<path class="ic" d="M37 15A16 16 0 1 0 40 30"/><path class="ic-fill" d="M43 11l-1.5 9.5-8-5z"/>'
           f'<path class="ic-acc-fill" d="M24 14.5{STAR}"/>'),
    "docker": ('<rect x="4" y="15" width="40" height="24" rx="2.5" class="ic"/>'
               '<path class="ic-thin" d="M11 19v16 M17.5 19v16 M24 19v16 M30.5 19v16 M37 19v16"/>'
               '<path class="ic" d="M15 15V9h18v6"/>'),
    "ros": ('<path class="ic-thin" d="M11 12L37 12 M11 12L24 36 M37 12L24 36"/>'
            '<circle cx="11" cy="12" r="5.5" class="ic-dot"/><circle cx="37" cy="12" r="5.5" class="ic-dot"/>'
            '<circle cx="24" cy="36" r="5.5" class="ic-dot"/>'
            '<path class="ic-acc" d="M24 36h14 M24 36v-12"/><path class="ic-acc-fill" d="M43 36l-6-3.5v7z"/>'),
    "mpl": ('<path class="ic" d="M6 5v37h37"/>'
            '<rect x="12" y="28" width="6" height="14" class="ic-soft"/><rect x="22" y="22" width="6" height="20" class="ic-soft"/>'
            '<rect x="32" y="15" width="6" height="27" class="ic-soft"/>'
            '<path class="ic-acc" d="M11 31L20 21L28 26L40 9"/>'),
    "plotjuggler": ('<rect x="3" y="7" width="42" height="33" rx="3.5" class="ic"/>'
                    '<path class="ic" d="M8 24c3-9 7-9 10 0s7 9 10 0 7-9 10 0"/>'
                    '<path class="ic-acc" d="M8 31c3-3 7-3 10 0s7 3 10 0 7-3 10 0"/>'),
    "numpy": ('<path class="ic" d="M12 6H6v36h6 M36 6h6v36h-6"/>'
              + "".join(f'<circle cx="{x}" cy="{y}" r="2.8" class="ic-fill"/>'
                        for x in (15, 24, 33) for y in (14, 24, 34))
              .replace('cx="24" cy="24" r="2.8" class="ic-fill"', 'cx="24" cy="24" r="3.6" class="ic-acc-fill"')),
    "scipy": ('<path class="ic" d="M6 5v37h37"/><path class="ic" d="M10 10C18 46 30 46 41 9"/>'
              '<circle cx="24.5" cy="36" r="3.8" class="ic-acc-fill"/>'),
    "opencv": ('<path class="ic" d="M3 24C12 11 36 11 45 24C36 37 12 37 3 24Z"/>'
               '<circle cx="24" cy="24" r="7.5" class="ic"/><circle cx="24" cy="24" r="3.2" class="ic-acc-fill"/>'),
    "torch": ("".join(f'<path class="ic-thin" d="M8 {a}L24 {b}"/>' for a in (12, 24, 36) for b in (8, 19, 29, 40))
              + "".join(f'<path class="ic-thin" d="M24 {b}L40 {c}"/>' for b in (8, 19, 29, 40) for c in (18, 30))
              + "".join(f'<circle cx="8" cy="{a}" r="3.6" class="ic-dot"/>' for a in (12, 24, 36))
              + "".join(f'<circle cx="24" cy="{b}" r="3.6" class="ic-dot"/>' for b in (8, 19, 29, 40))
              + '<circle cx="40" cy="18" r="3.8" class="ic-acc-fill"/><circle cx="40" cy="30" r="3.6" class="ic-dot"/>'),
    "gym": ('<rect x="4" y="4" width="40" height="40" rx="3.5" class="ic"/>'
            '<path class="ic-thin" d="M17.3 4v40 M30.7 4v40 M4 17.3h40 M4 30.7h40"/>'
            '<path class="ic-acc ic-dash" d="M10.7 37.3V24h13.3V10.7h10"/>'
            '<circle cx="10.7" cy="37.3" r="4" class="ic-fill"/>'
            f'<path class="ic-acc-fill" d="M37.3 5{STAR}"/>'),
}


def icon(key, cx, cy, scale=1.0):
    half = 24 * scale
    return f'<g transform="translate({cx - half:.1f},{cy - half:.1f}) scale({scale})">{ICONS[key]}</g>'


# ---------------------------------------------------------------------------
# Poster layout (poster coordinates; the static SVG adds a title above)
# ---------------------------------------------------------------------------

LEFT, RIGHT = 52, 1228
METHOD_W, METHOD_H, METHOD_TOP = 138, 150, 12
TOOL_W, TOOL_H, TOOL_TOP = 123, 120, 236
PART_W, PART_H, PART_TOP = 200, 62, 426
SCENE_TOP, SCENE_BOTTOM = 498, 950
POSTER_H = 958


def method_x(key):
    return LEFT + METHOD_W / 2 + METHOD_ORDER.index(key) * (METHOD_W + 10)


def tool_x(key):
    return LEFT + TOOL_W / 2 + TOOL_ORDER.index(key) * (TOOL_W + 8)


def method_card(key):
    m = METHODS[key]
    cx, top = method_x(key), METHOD_TOP
    x0 = cx - METHOD_W / 2
    out = [node_open(key, "method", f"{m['title']} {m['sub']}, outcome {m['outcome']}")]
    out.append(f'<rect x="{x0:.1f}" y="{top}" width="{METHOD_W}" height="{METHOD_H}" rx="12" class="card"/>')
    out.append(f'<circle cx="{cx:.1f}" cy="{top + 46}" r="31" class="tint"/>')
    out.append(icon(key, cx, top + 46, 0.9))
    out.append(f'<circle cx="{x0 + 17:.1f}" cy="{top + 17}" r="10" class="badge"/>')
    out.append(text(x0 + 17, top + 21.5, str(m["outcome"]), "t-badge"))
    out.append(text(cx, top + 100, esc(m["title"]), "t-card"))
    out.append(text(cx, top + 117, esc(m["sub"]), "t-tag"))
    chip_w = 9 + 6.4 * len(m["hw"])
    out.append(f'<rect x="{cx - chip_w / 2:.1f}" y="{top + 126}" width="{chip_w:.1f}" height="17" rx="8.5" class="chip"/>')
    out.append(text(cx, top + 138.5, esc(m["hw"]), "t-chip"))
    out.append("</g>")
    return out


def tool_card(key):
    t = TOOLS[key]
    cx, top = tool_x(key), TOOL_TOP
    x0 = cx - TOOL_W / 2
    out = [node_open(key, "tool", t["name"])]
    out.append(f'<rect x="{x0:.1f}" y="{top}" width="{TOOL_W}" height="{TOOL_H}" rx="12" class="card"/>')
    out.append(f'<rect x="{cx - 28:.1f}" y="{top + 10}" width="56" height="48" rx="12" class="tint"/>')
    out.append(icon(key, cx, top + 34, 0.78))
    out.append(text(cx, top + 77, esc(t["name"]), "t-card t-tool" + (" t-long" if len(t["name"]) > 13 else "")))
    out.append(text(cx, top + 93, esc(t["tag"]), "t-tag"))
    out.append(text(cx, top + 110, esc(t["used"]), "t-used"))
    out.append("</g>")
    return out


def part_card(key):
    p = PARTS[key]
    cx, top = p["x"], PART_TOP
    x0 = cx - PART_W / 2
    out = [node_open(key, "part", p["name"])]
    out.append(f'<rect x="{x0:.1f}" y="{top}" width="{PART_W}" height="{PART_H}" rx="12" class="card"/>')
    out.append(f'<circle cx="{x0 + 24:.1f}" cy="{top + 31}" r="13" class="pin-dot"/>')
    out.append(text(x0 + 24, top + 36, str(p["num"]), "t-pin"))
    out.append(text(x0 + 46, top + 28, esc(p["name"]), "t-card", "start"))
    out.append(text(x0 + 46, top + 46, esc(p["sub"]), "t-part", "start"))
    out.append("</g>")
    return out


def built_with(m):
    return METHODS[m]["tools"]


def used_with(m):
    return [t for t in TOOL_ORDER if m in USED_WITH.get(t, [])]


def edges():
    """Curves from ideas to tools (solid: built with; dotted: used with),
    and from tools to parts of the robot."""
    out = []
    pairs = [(m, t) for m in METHOD_ORDER for t in built_with(m) + used_with(m)]
    dotted = {(m, t) for m in METHOD_ORDER for t in used_with(m)}
    tool_parts = [(t, p) for t in TOOL_ORDER for p in TOOLS[t]["parts"] if p in PARTS]

    def anchors(items, key_of, x_of):
        groups = {}
        for item in items:
            groups.setdefault(key_of(item), []).append(item)
        place = {}
        for key, group in groups.items():
            group.sort(key=x_of)
            for item, x in zip(group, spread(x_of_key[key], len(group))):
                place[item] = x
        return place

    x_of_key = {**{m: method_x(m) for m in METHOD_ORDER}, **{t: tool_x(t) for t in TOOL_ORDER},
                **{p: PARTS[p]["x"] for p in PARTS}}
    m_bottom = anchors(pairs, lambda e: e[0], lambda e: x_of_key[e[1]])
    t_top = anchors(pairs, lambda e: e[1], lambda e: x_of_key[e[0]])
    t_bottom = anchors(tool_parts, lambda e: e[0], lambda e: x_of_key[e[1]])
    p_top = anchors(tool_parts, lambda e: e[1], lambda e: x_of_key[e[0]])
    # Dotted lines first, so the solid "built with" lines sit on top.
    for pair in sorted(pairs, key=lambda e: e not in dotted):
        d = curve(m_bottom[pair], METHOD_TOP + METHOD_H, t_top[pair], TOOL_TOP)
        cls = "edge e-idea e-use" if pair in dotted else "edge e-idea"
        out.append(f'<path d="{d}" class="{cls}" data-ends="{pair[0]} {pair[1]}"/>')
    for pair in tool_parts:
        d = curve(t_bottom[pair], TOOL_TOP + TOOL_H, p_top[pair], PART_TOP)
        out.append(f'<path d="{d}" class="edge e-tool" data-ends="{pair[0]} {pair[1]}"/>')
    return out


def row_labels():
    out = []
    rows = [("THE IDEAS", METHOD_TOP, METHOD_TOP + METHOD_H, "r-idea"),
            ("THE TOOLS", TOOL_TOP, TOOL_TOP + TOOL_H, "r-tool"),
            ("THE ROBOT", PART_TOP, SCENE_BOTTOM, "r-robot")]
    for label, top, bottom, cls in rows:
        middle = (top + bottom) / 2
        out.append(f'<rect x="36" y="{top}" width="5" height="{bottom - top}" rx="2.5" class="{cls}"/>')
        out.append(f'<text transform="translate(26,{middle}) rotate(-90)" class="t-row {cls}-text" text-anchor="middle">{label}</text>')
    gap1 = (METHOD_TOP + METHOD_H + TOOL_TOP) / 2
    gap2 = (TOOL_TOP + TOOL_H + PART_TOP) / 2
    out.append(f'<path d="M14,{gap1 - 6} h20" class="edge e-idea key-line"/>')
    out.append(text(38, gap1 - 2, "built with", "t-gap", "start"))
    out.append(f'<path d="M14,{gap1 + 12} h20" class="edge e-idea e-use key-line"/>')
    out.append(text(38, gap1 + 16, "used with", "t-gap", "start"))
    out.append(text(14, gap2 + 4, "works with", "t-gap", "start"))
    return out


# ---------------------------------------------------------------------------
# The illustrated conveyor cell. World coordinates in pixels: x along the
# belt, y away from the viewer, z up. The view looks down a little: a point
# moves up the page by z plus 0.45 of its depth.
# ---------------------------------------------------------------------------

DEPTH = 0.45
FLOOR = 920


def P(x, y, z):
    return x, FLOOR - z - DEPTH * y


def pts(points):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in points)


def block(x0, y0, z0, dx, dy, dz, cls):
    """A box seen from the front and above: its front and top faces."""
    front = [P(x0, y0, z0), P(x0 + dx, y0, z0), P(x0 + dx, y0, z0 + dz), P(x0, y0, z0 + dz)]
    top = [P(x0, y0, z0 + dz), P(x0 + dx, y0, z0 + dz), P(x0 + dx, y0 + dy, z0 + dz), P(x0, y0 + dy, z0 + dz)]
    return f'<polygon points="{pts(front)}" class="{cls}-front"/><polygon points="{pts(top)}" class="{cls}-top"/>'


def cylinder(x, y, z0, height, radius, cls, open_top=False):
    cx, bottom = P(x, y, z0)
    _, top = P(x, y, z0 + height)
    ry = radius * DEPTH
    out = (f'<path d="M{cx - radius:.1f},{top:.1f} L{cx - radius:.1f},{bottom:.1f} '
           f'A{radius},{ry:.1f} 0 0 0 {cx + radius:.1f},{bottom:.1f} L{cx + radius:.1f},{top:.1f} Z" class="{cls}-side"/>'
           f'<ellipse cx="{cx:.1f}" cy="{top:.1f}" rx="{radius}" ry="{ry:.1f}" class="{cls}-top"/>')
    if open_top:
        out += f'<ellipse cx="{cx:.1f}" cy="{top + 1:.1f}" rx="{radius - 5}" ry="{(radius - 5) * DEPTH:.1f}" class="{cls}-inner"/>'
    return out


def triangle_part(x, y, z0, size, height, cls):
    half, reach = size / 2, size * 0.43
    front = [P(x - half, y - reach, z0), P(x + half, y - reach, z0),
             P(x + half, y - reach, z0 + height), P(x - half, y - reach, z0 + height)]
    top = [P(x - half, y - reach, z0 + height), P(x + half, y - reach, z0 + height), P(x, y + reach, z0 + height)]
    return f'<polygon points="{pts(front)}" class="{cls}-front"/><polygon points="{pts(top)}" class="{cls}-top"/>'


def belt_part(shape, color, x, y):
    z0, size, height = 110, 40, 10
    if shape == "square":
        return block(x - size / 2, y - size / 2, z0, size, size, height, f"obj-{color}")
    if shape == "circle":
        return cylinder(x, y, z0, height, size / 2, f"obj-{color}")
    return triangle_part(x, y, z0, size, height, f"obj-{color}")


def line(a, b, cls, width):
    return f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" class="{cls}" stroke-width="{width}"/>'


TOPIC_DEFS = ('<defs><marker id="topic-arrow" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="4.2" '
              'markerHeight="4.2" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" class="topic-head"/>'
              '</marker></defs>')


def laptop_screen(x, y, w, h):
    """Two windows on the laptop: RViz with the arm over the belt (left) and
    PlotJuggler with two joint signals (right)."""
    out = []
    gap, bar = 5, 9
    win = (w - gap) / 2
    for k, cls in enumerate(("screen-a", "screen-b")):
        wx = x + k * (win + gap)
        out.append(f'<rect x="{wx:.1f}" y="{y:.1f}" width="{win:.1f}" height="{h:.1f}" rx="2" class="{cls}"/>')
        out.append(f'<rect x="{wx:.1f}" y="{y:.1f}" width="{win:.1f}" height="{bar}" rx="2" class="screen-bar"/>')
        for d in range(3):
            out.append(f'<circle cx="{wx + 5 + 4.5 * d:.1f}" cy="{y + 4.5:.1f}" r="1.5" class="screen-dot"/>')
    top, bottom = y + bar, y + h
    left, right = x, x + win
    # RViz: floor grid, the belt with parts, and the arm reaching from its base.
    for k in range(4):
        gy = top + (bottom - top) * (0.5 + 0.15 * k)
        out.append(f'<line x1="{left + 3:.1f}" y1="{gy:.1f}" x2="{right - 3:.1f}" y2="{gy:.1f}" class="screen-grid"/>')
    for k in range(5):
        gx = left + 8 + (win - 16) * k / 4
        out.append(f'<line x1="{gx:.1f}" y1="{top + (bottom - top) * 0.5:.1f}" x2="{gx:.1f}" y2="{bottom - 3:.1f}" class="screen-grid"/>')
    belt_top = top + (bottom - top) * 0.62
    out.append(f'<rect x="{left + 3:.1f}" y="{belt_top:.1f}" width="{win - 6:.1f}" height="13" class="screen-belt"/>')
    out.append(f'<rect x="{left + 9:.1f}" y="{belt_top + 3:.1f}" width="6" height="6" class="sh-blue"/>')
    out.append(f'<circle cx="{left + 44:.1f}" cy="{belt_top + 7:.1f}" r="3.4" class="sh-red"/>')
    out.append(f'<path d="M{left + 57:.1f},{belt_top + 10:.1f} l3.5,-7 l3.5,7z" class="sh-yellow"/>')
    base = (left + 26, top + (bottom - top) * 0.3)
    arm = [base, (base[0] - 12, base[1] + 12), (base[0] + 3, base[1] + 20), (base[0] + 12, base[1] + 25),
           (left + 44, belt_top + 6)]
    out.append(f'<ellipse cx="{base[0]:.1f}" cy="{base[1] + 2:.1f}" rx="6" ry="3.2" class="screen-base"/>')
    for k, width in enumerate((4, 3.4, 2.8, 2.2)):
        a, b = arm[k], arm[k + 1]
        out.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" class="screen-link" stroke-width="{width}"/>')
    for a in arm[1:4]:
        out.append(f'<circle cx="{a[0]:.1f}" cy="{a[1]:.1f}" r="1.6" class="screen-joint"/>')
    bx, by = base
    out.append(f'<path d="M{bx:.1f},{by:.1f} h9" class="screen-ax-x"/><path d="M{bx:.1f},{by:.1f} v-9" class="screen-ax-z"/>'
               f'<path d="M{bx:.1f},{by:.1f} l6,-4" class="screen-ax-y"/>')
    # PlotJuggler: axes and two joint signals over time.
    px0, px1 = right + gap + 5, x + w - 4
    out.append(f'<path d="M{px0:.1f},{top + 5:.1f} V{bottom - 5:.1f} H{px1:.1f}" class="screen-axis"/>')
    count = 24
    wave1 = " ".join(f"{px0 + (px1 - px0) * i / count:.1f},{top + 26 - 14 * ((-1) ** (i // 6)) * (1 if i % 6 else 0.2):.1f}" for i in range(count + 1))
    wave2 = " ".join(f"{px0 + (px1 - px0) * i / count:.1f},{bottom - 20 - 9 * ((i % 12) / 12):.1f}" for i in range(count + 1))
    out.append(f'<polyline points="{wave1}" class="screen-wave1"/><polyline points="{wave2}" class="screen-wave2"/>')
    return out


def draw_scene():
    out = [TOPIC_DEFS, f'<rect x="{LEFT}" y="{SCENE_TOP}" width="{RIGHT - LEFT}" height="{SCENE_BOTTOM - SCENE_TOP}" rx="16" class="scene-wall"/>',
           f'<path d="M{LEFT},{FLOOR - 62} H{RIGHT} V{SCENE_BOTTOM - 16} a16,16 0 0 1 -16,16 H{LEFT + 16} '
           f'a16,16 0 0 1 -16,-16 Z" class="scene-floor"/>']
    # Shadows on the floor.
    out.append(f'<ellipse cx="750" cy="{FLOOR - 26}" rx="450" ry="26" class="shadow"/>')
    out.append(f'<ellipse cx="150" cy="{FLOOR - 24}" rx="120" ry="20" class="shadow"/>')

    # Behind the belt: the overhead camera's pole and the arm's column.
    pole_x, pole_y, pole_h = 1080, 240, 260
    out.append('<g class="node k-part" data-id="fixedcam">')
    out.append(cylinder(pole_x, pole_y, 0, pole_h, 7, "pole"))
    out.append("</g>")
    base_x, base_y, arm_z = 600, 300, 200
    out.append('<g class="node k-part" data-id="arm">')
    out.append(cylinder(base_x, base_y, 0, arm_z - 12, 26, "column"))
    out.append("</g>")

    # Bins on a shelf between the arm and the belt.
    out.append(block(400, 175, 90, 400, 60, 10, "shelf"))
    for name, bx in (("A", 470), ("B", 730)):
        out.append(cylinder(bx, 205, 100, 46, 32, "bin", open_top=True))
        bx_s, by_s = P(bx, 205, 118)
        out.append(text(bx_s, by_s + 4, name, "t-bin"))

    # Desk and laptop.
    out.append('<g class="node k-part" data-id="computer">')
    for lx in (52, 250):
        out.append(block(lx, 20, 0, 8, 8, 92, "leg"))
    out.append(block(40, 10, 92, 230, 110, 8, "desk"))
    out.append(block(78, 28, 100, 156, 72, 6, "laptop"))
    sx0, sy_bottom = P(78, 100, 106)
    _, sy_top = P(78, 100, 214)
    w, h = 156, sy_bottom - sy_top
    out.append(f'<rect x="{sx0:.1f}" y="{sy_top:.1f}" width="{w}" height="{h:.1f}" rx="6" class="screen-bezel"/>')
    out += laptop_screen(sx0 + 6, sy_top + 6, w - 12, h - 12)
    out.append("</g>")

    # The conveyor: legs, belt, and the parts riding on it.
    out.append('<g class="node k-part" data-id="conveyor">')
    for lx in (350, 1140):
        out.append(block(lx, 118, 0, 10, 8, 88, "leg"))
        out.append(block(lx, 2, 0, 10, 8, 88, "leg"))
    belt_x0, belt_x1, belt_depth, belt_z = 320, 1180, 130, 110
    out.append(block(belt_x0, 0, belt_z - 24, belt_x1 - belt_x0, belt_depth, 24, "frame"))
    top = [P(belt_x0 + 4, 4, belt_z), P(belt_x1 - 4, 4, belt_z), P(belt_x1 - 4, belt_depth - 4, belt_z), P(belt_x0 + 4, belt_depth - 4, belt_z)]
    out.append(f'<polygon points="{pts(top)}" class="belt"/>')
    for sx in range(belt_x0 + 34, belt_x1 - 10, 46):
        a, b = P(sx, 6, belt_z), P(sx, belt_depth - 6, belt_z)
        out.append(line(a, b, "belt-seam", 1.4))
    for sx in range(belt_x0 + 70, belt_x1 - 40, 120):  # direction chevrons on the frame
        cx, cy = P(sx, 0, belt_z - 12)
        out.append(f'<path d="M{cx + 5:.1f},{cy - 5:.1f} l-6,5 l6,5" class="chevron"/>')
    for shape, color, x, y in (("square", "blue", 430, 52), ("circle", "red", 676, 98),
                               ("triangle", "yellow", 850, 72), ("circle", "blue", 960, 44),
                               ("square", "red", 1080, 80)):
        out.append(belt_part(shape, color, x, y))
    out.append("</g>")
    lx, ly = P(760, 0, 0)
    out.append(text(lx, ly - 52, "parts arrive from the right, every 3.3 s, on a 0.06 m/s belt", "t-scene"))
    blx, bly = P(772, 205, 130)
    out.append(text(blx, bly, "sort into bins", "t-scene", "start"))

    # Overhead camera: boom, body, and what it sees.
    cam = (1010, 62, pole_h - 20)
    out.append('<g class="node k-part" data-id="fixedcam">')
    foot = [P(925, 8, belt_z), P(1105, 8, belt_z), P(1105, 124, belt_z), P(925, 124, belt_z)]
    lens = P(cam[0], cam[1], cam[2] - 4)
    out.append(f'<polygon points="{pts([lens, foot[0], foot[1]])}" class="cone"/>')
    out.append(f'<polygon points="{pts(foot)}" class="footprint"/>')
    out.append(line(P(pole_x, pole_y, pole_h - 4), P(cam[0] + 6, cam[1], pole_h - 4), "boom", 7))
    out.append(block(cam[0] - 16, cam[1] - 10, cam[2], 32, 20, 18, "cam"))
    lx, ly = lens
    out.append(f'<ellipse cx="{lx:.1f}" cy="{ly + 1:.1f}" rx="7" ry="3.5" class="lens"/>')
    out.append("</g>")

    # The arm: four links in a plane above the belt, a suction cup on a
    # vertical stroke, and the wrist camera on the last link.
    joints = [(base_x, base_y), (510, 220), (590, 180), (640, 145), (676, 98)]
    screen = [P(x, y, arm_z) for x, y in joints]
    out.append('<g class="node k-part" data-id="arm">')
    out.append(cylinder(base_x, base_y, arm_z - 12, 22, 30, "hub"))
    widths = [20, 17, 14, 12]
    for k in range(4):
        out.append(line(screen[k], screen[k + 1], "link-edge", widths[k] + 5))
    for k in range(4):
        out.append(line(screen[k], screen[k + 1], "link", widths[k]))
    for k, (x, y) in enumerate(joints[1:4]):
        out.append(cylinder(x, y, arm_z - 6, 12, 11 - k, "joint"))
    tx, ty = joints[-1]
    out.append(cylinder(tx, ty, arm_z - 8, 16, 10, "joint"))
    out.append(line(P(tx, ty, arm_z - 8), P(tx, ty, 138), "rod", 6))
    out.append(cylinder(tx, ty, 128, 10, 10, "cup"))
    out.append("</g>")
    wx, wy = 655, 125
    out.append('<g class="node k-part" data-id="toolcam">')
    look = P(684, 92, belt_z)
    body = P(wx, wy, arm_z - 10)
    out.append(f'<polygon points="{pts([body, (look[0] - 30, look[1]), (look[0] + 30, look[1])])}" class="cone"/>')
    out.append(f'<ellipse cx="{look[0]:.1f}" cy="{look[1]:.1f}" rx="30" ry="{30 * DEPTH:.1f}" class="footprint"/>')
    out.append(block(wx - 10, wy - 7, arm_z - 14, 20, 14, 14, "cam"))
    out.append(f'<ellipse cx="{body[0]:.1f}" cy="{body[1] + 4:.1f}" rx="5" ry="2.5" class="lens"/>')
    out.append("</g>")

    # ROS 2 topics: dashed arrows labeled with each topic's name. Paths run
    # left to right so the names read upright; the arrowhead shows which way
    # the messages flow.
    out.append('<g class="node k-part" data-id="cable">')
    topics = [("topic-img", "M110,661 Q560,420 994,640", "in", "fixed_camera/image_raw", "76%"),
              ("topic-cmd", "M214,661 Q380,560 568,582", "out", "joint_velocity_command", "50%"),
              ("topic-js", "M234,692 Q400,640 572,598", "in", "joint_states", "50%")]
    for path_id, d, way, name, offset in topics:
        marker = 'marker-start="url(#topic-arrow)"' if way == "in" else 'marker-end="url(#topic-arrow)"'
        out.append(f'<path id="{path_id}" d="{d}" class="ros-link flow-{way}" {marker}/>')
        out.append(f'<text class="t-topic" dy="-6"><textPath href="#{path_id}" startOffset="{offset}" '
                   f'text-anchor="middle">{name}</textPath></text>')
    out.append("</g>")
    key_y = SCENE_TOP + 26
    out.append(f'<path d="M{LEFT + 18},{key_y - 4} h36" class="ros-link" marker-end="url(#topic-arrow)"/>')
    out.append(text(LEFT + 64, key_y, "ROS 2 topic: messages flow in the arrow's direction", "t-ros", "start"))

    # Numbered pins that match the cards above the scene.
    pins = {"computer": (64, 662), "arm": (474, 646), "toolcam": (622, 690), "fixedcam": (1052, 640)}
    for key, (x, y) in pins.items():
        out.append(f'<g class="node k-part pin" data-id="{key}">'
                   f'<circle cx="{x}" cy="{y}" r="13" class="pin-dot"/>{text(x, y + 5, str(PARTS[key]["num"]), "t-pin")}</g>')

    out.append(text(RIGHT - 18, SCENE_BOTTOM - 14, "SIMULATED IN THIS COURSE · THE SAME CODE RUNS ON REAL HARDWARE",
                    "t-scene-tag", "end"))
    return out


def draw_poster():
    out = row_labels()
    out += edges()
    for key in METHOD_ORDER:
        out += method_card(key)
    for key in TOOL_ORDER:
        out += tool_card(key)
    out += draw_scene()
    for key in PART_ORDER:
        out += part_card(key)
    return out


def draw_grid():
    """Where each tool appears, as a row per tool and a column per assignment."""
    out = []
    label_width = 190
    column_width = (WIDTH - 24 - label_width) / len(COLUMNS)
    row_height = 26
    out.append(text(16, 22, "Where each tool comes back", "t-grid-title", "start"))
    out.append('<circle cx="22" cy="38" r="5" class="dot"/>')
    out.append(text(32, 42, "you use it", "t-gap", "start"))
    out.append('<circle cx="110" cy="38" r="5" class="ring"/>')
    out.append(text(120, 42, "optional or planned", "t-gap", "start"))
    header_y = 66
    for index, column in enumerate(COLUMNS):
        x = label_width + column_width * (index + 0.5)
        out.append(text(x, header_y, column, "t-grid-head"))
        out.append(text(x, header_y + 13, WEEKS[index], "t-gap"))
    first_row = header_y + 24
    for row, key in enumerate(TOOL_ORDER):
        y = first_row + row * row_height
        name = TOOLS[key]["name"]
        out.append(f'<g class="node grid-row" data-id="{key}" tabindex="0" role="button" aria-label="{esc(name)}">')
        out.append(f'<rect x="8" y="{y}" width="{WIDTH - 16}" height="{row_height}" rx="5" class="grid-band"/>')
        out.append(text(18, y + 17.5, esc(name), "t-grid-label", "start"))
        for index, column in enumerate(COLUMNS):
            level = USAGE[key].get(column, 0)
            if level:
                x = label_width + column_width * (index + 0.5)
                note = USAGE_NOTES.get((key, column), "used")
                cls = "dot" if level == 2 else "ring"
                out.append(f'<circle cx="{x:.1f}" cy="{y + 13}" r="6" class="{cls}"><title>{esc(name)}, {column}: {esc(note)}</title></circle>')
        out.append("</g>")
    return out, first_row + len(TOOL_ORDER) * row_height + 10


# ---------------------------------------------------------------------------
# Styles. The scene keeps fixed colors in both themes; everything else uses
# tokens on the interactive page and light values in the static SVG.
# ---------------------------------------------------------------------------

SCENE_CSS = """
.shadow { fill: #000; opacity: .10; }
.leg-front { fill: #8a95a1; } .leg-top { fill: #a8b2bd; }
.frame-front { fill: #b7c1cb; } .frame-top { fill: #d3dae1; }
.belt { fill: #39414a; } .belt-seam { stroke: #4b545e; }
.chevron { fill: none; stroke: #6f7b88; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }
.desk-front { fill: #a98058; } .desk-top { fill: #c99f75; }
.laptop-front { fill: #8f99a4; } .laptop-top { fill: #c3cad2; }
.screen-bezel { fill: #1c2127; } .screen-a { fill: #2b323b; } .screen-b { fill: #f3f5f7; }
.screen-bar { fill: #4a5561; } .screen-dot { fill: #c3cad2; }
.screen-grid { stroke: #414b56; stroke-width: .8; } .screen-belt { fill: #5d6772; }
.screen-base { fill: #8a949e; } .screen-link { stroke: #f28c28; stroke-linecap: round; } .screen-joint { fill: #2b3137; }
.screen-axis { fill: none; stroke: #8a949e; stroke-width: 1; }
.screen-ax-x { stroke: #e0483a; stroke-width: 2; } .screen-ax-y { stroke: #2fa84f; stroke-width: 2; }
.screen-ax-z { stroke: #4a7fe6; stroke-width: 2; }
.screen-arm { fill: none; stroke: #f28c28; stroke-width: 4; stroke-linecap: round; stroke-linejoin: round; }
.screen-wave1 { fill: none; stroke: #1f8fbf; stroke-width: 1.8; } .screen-wave2 { fill: none; stroke: #e0552b; stroke-width: 1.8; }
.shelf-front { fill: #a9b2bc; } .shelf-top { fill: #cdd4db; }
.bin-side { fill: #5b7b96; } .bin-top { fill: #7f9db7; } .bin-inner { fill: #2c3c4a; }
.column-side { fill: #4a535d; } .column-top { fill: #67717c; }
.hub-side { fill: #3b434c; } .hub-top { fill: #59636e; }
.pole-side { fill: #8f9aa6; } .pole-top { fill: #b2bcc6; }
.boom { stroke: #8f9aa6; stroke-linecap: round; }
.link-edge { stroke: #9c4e0d; stroke-linecap: round; } .link { stroke: #f28c28; stroke-linecap: round; }
.joint-side { fill: #2b3137; } .joint-top { fill: #8a949e; }
.rod { stroke: #8a949e; stroke-linecap: round; }
.cup-side { fill: #23292f; } .cup-top { fill: #3b434c; }
.cam-front { fill: #1f242a; } .cam-top { fill: #3a424b; } .lens { fill: #4a8de0; }
.cone { fill: #4a8de0; opacity: .15; }
.footprint { fill: #4a8de0; fill-opacity: .14; stroke: #4a8de0; stroke-width: 1.3; stroke-dasharray: 5 4; }
.obj-red-front, .obj-red-side { fill: #a12424; } .obj-red-top { fill: #d23b36; }
.obj-blue-front, .obj-blue-side { fill: #23409e; } .obj-blue-top { fill: #3b62d6; }
.obj-yellow-front, .obj-yellow-side { fill: #b9971c; } .obj-yellow-top { fill: #ecc93a; }
.ros-link { fill: none; stroke: #d68a12; stroke-width: 2.6; stroke-dasharray: 8 6; }
.topic-head { fill: #d68a12; }
.t-bin { font-size: 12px; font-weight: 700; fill: #e8eef4; }
"""

STATIC_CSS = """
text { font-family: "IBM Plex Sans", "Segoe UI", Arial, sans-serif; fill: #18222d; }
.card { fill: #ffffff; stroke: #d3d9e0; stroke-width: 1.2; }
.k-method { color: #0b7a72; } .k-tool { color: #3653b5; }
.k-method .tint { fill: #e1f3f1; } .k-tool .tint { fill: #e7ecfb; }
.badge { fill: #0b7a72; } .t-badge { fill: #ffffff; font-size: 11.5px; font-weight: 700; }
.chip { fill: #e1f3f1; } .t-chip { font-size: 11px; font-weight: 600; fill: #0b5f59; }
.t-card { font-family: Archivo, "IBM Plex Sans", Arial, sans-serif; font-size: 15px; font-weight: 700; }
.t-tool { font-size: 14px; } .t-long { font-size: 12.5px; }
.t-tag { font-size: 11.5px; fill: #4f5b67; }
.t-used { font-size: 11px; font-weight: 600; fill: #3653b5; }
.t-part { font-size: 11.5px; fill: #4f5b67; }
.pin-dot { fill: #e0552b; stroke: #ffffff; stroke-width: 2; } .t-pin { fill: #ffffff; font-size: 13px; font-weight: 700; }
.r-idea { fill: #0b7a72; } .r-tool { fill: #3653b5; } .r-robot { fill: #e0552b; }
.t-row { font-family: Archivo, Arial, sans-serif; font-size: 13px; font-weight: 800; letter-spacing: .14em; }
.r-idea-text { fill: #0b7a72; } .r-tool-text { fill: #3653b5; } .r-robot-text { fill: #e0552b; }
.t-gap { font-size: 11px; font-style: italic; fill: #66727e; }
.edge { fill: none; stroke-width: 1.8; stroke-linecap: round; }
.e-idea { stroke: #0b7a72; opacity: .38; } .e-tool { stroke: #3653b5; opacity: .38; }
.e-use { stroke-width: 1.4; stroke-dasharray: 1.5 4; opacity: .55; } .key-line { opacity: .8; }
.t-topic { font-family: "IBM Plex Mono", Consolas, monospace; font-size: 12px; font-weight: 600; fill: #a8650a; }
.scene-wall { fill: #e8eef3; } .scene-floor { fill: #d9e1e8; }
.t-scene { font-size: 11.5px; fill: #4f5b67; font-style: italic; }
.t-ros { font-size: 12px; font-weight: 700; fill: #b06f0a; }
.t-scene-tag { font-size: 11px; font-weight: 700; letter-spacing: .1em; fill: #4f5b67; }
.ic { fill: none; stroke: currentColor; stroke-width: 2.6; stroke-linecap: round; stroke-linejoin: round; }
.ic-thin { fill: none; stroke: currentColor; stroke-width: 1.3; opacity: .6; }
.ic-fill { fill: currentColor; } .ic-soft { fill: currentColor; opacity: .22; }
.ic-dot { fill: #ffffff; stroke: currentColor; stroke-width: 2.2; }
.ic-dash { stroke-dasharray: 4 3.5; }
.ic-acc { fill: none; stroke: #e0552b; stroke-width: 2.6; stroke-linecap: round; stroke-linejoin: round; }
.ic-acc-fill { fill: #e0552b; }
.ax-x { stroke: #d8402f; } .ax-xf { fill: #d8402f; } .ax-y { stroke: #23974a; } .ax-yf { fill: #23974a; }
.ax-z { stroke: #2f62cf; } .ax-zf { fill: #2f62cf; }
.sh-red { fill: #d23b36; } .sh-blue { fill: #3b62d6; } .sh-yellow { fill: #e2bb22; }
.t-head { font-family: Archivo, Arial, sans-serif; font-size: 30px; font-weight: 800; }
.t-lede { font-size: 14px; fill: #3d4955; }
.t-sub-head { font-family: Archivo, Arial, sans-serif; font-size: 21px; font-weight: 700; fill: #e0552b; }
.t-cite { font-size: 12.5px; font-style: italic; fill: #66727e; }
"""

# ---------------------------------------------------------------------------
# Static SVG
# ---------------------------------------------------------------------------


def write_static():
    header = 112
    height = header + POSTER_H
    body = [f'<rect width="{WIDTH}" height="{height}" fill="#f5f7f9"/>',
            text(LEFT - 38, 40, 'Line upon Line<tspan class="t-sub-head" dx="16">From rotation matrices to a robot '
                 'that sees, decides, and acts.</tspan>', "t-head", "start"),
            text(LEFT - 38, 62, "“Line upon line, precept upon precept.” 2 Nephi 28:30", "t-cite", "start"),
            text(LEFT - 38, 88, "Conveyor sorting project: each idea you learn is built with a tool, and each tool works "
                 "with a part of the robot. You simulate the cell; the same code runs on real hardware.", "t-lede", "start"),
            f'<g transform="translate(0,{header})">', *draw_poster(), "</g>"]
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}" width="{WIDTH}" height="{height}" '
           f'role="img" aria-label="Course ideas, the tools that build them, and the robot hardware each tool works with">'
           f"<style>{STATIC_CSS}{SCENE_CSS}</style>" + "".join(body) + "</svg>\n")
    (HERE / "robot_stack.svg").write_text(svg, encoding="utf-8")


# ---------------------------------------------------------------------------
# Interactive page
# ---------------------------------------------------------------------------


def lit_sets():
    """For each item, the ideas, tools, and parts that light up with it."""
    uses = {t: [m for m in METHOD_ORDER if t in built_with(m) + used_with(m)] for t in TOOL_ORDER}
    builds = {t: [m for m in METHOD_ORDER if t in built_with(m)] for t in TOOL_ORDER}
    touches = {p: [t for t in TOOL_ORDER if p in TOOLS[t]["parts"]] for p in list(PARTS) + ["cable"]}
    lit = {}
    for m in METHOD_ORDER:
        tools = built_with(m)
        lit[m] = [m] + tools + used_with(m) + [p for t in tools for p in TOOLS[t]["parts"]]
    for t in TOOL_ORDER:
        lit[t] = [t] + uses[t] + TOOLS[t]["parts"]
    for p in PARTS:
        lit[p] = [p] + touches[p] + [m for t in touches[p] for m in builds[t]]
    lit["cable"] = ["cable", "ros", "computer", "arm", "toolcam", "fixedcam"]
    lit["conveyor"] = ["conveyor"]
    return {k: sorted(set(v)) for k, v in lit.items()}


def detail_data():
    lit = lit_sets()
    data = {}
    for key, m in METHODS.items():
        data[key] = {"kind": f"Idea · course outcome {m['outcome']}", "name": f"{m['title']}: {m['sub']}",
                     "what": m["what"], "groups": [["Where you learn it", m["learn"]],
                                                   ["Built with", [TOOLS[t]["name"] for t in built_with(key)]],
                                                   ["Used with", [TOOLS[t]["name"] for t in used_with(key)]]],
                     "project": m["project"], "real": m["real"]}
    for key, t in TOOLS.items():
        ideas = [METHODS[m]["title"] for m in METHOD_ORDER if key in built_with(m)]
        alongside = [METHODS[m]["title"] for m in USED_WITH.get(key, [])]
        parts = [PARTS[p]["name"] for p in t["parts"] if p in PARTS]
        groups = [["Where you learn it", t["learn"]], ["Builds these ideas", ideas], ["Used with these ideas", alongside]]
        groups.append(["Works with", parts])
        data[key] = {"kind": "Tool", "name": t["name"], "what": t["what"], "groups": groups,
                     "project": t["project"], "real": t["real"], "reach": t["reach"], "beyond": t["beyond"]}
    for key, p in PARTS.items():
        tools = [TOOLS[t]["name"] for t in TOOL_ORDER if key in TOOLS[t]["parts"]]
        data[key] = {"kind": f"Part {p['num']} of the robot", "name": p["name"], "groups": [["Tools that work with it", tools]],
                     "course": p["simtext"], "real": p["realtext"]}
    for key, s in SCENERY.items():
        data[key] = {"kind": "Part of the robot cell", "name": s["name"], "course": s["simtext"], "real": s["realtext"]}
    data["cable"]["groups"] = [["Tools that work with it", ["ROS 2 + RViz"]]]
    for key in data:
        data[key]["on"] = lit[key]
    return data


PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Line upon Line</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@600;700;800&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap">
<style>
/* Layout: a header; the poster beside a detail panel (stacked when narrow); the reuse grid below. */
:root {
  --bg: #f4f6f8; --surface: #ffffff; --ink: #18222d; --muted: #55616d; --rule: #d3d9e0;
  --idea: #0b7a72; --idea-tint: #e1f3f1; --idea-ink: #0b5f59; --tool: #3653b5; --tool-tint: #e7ecfb;
  --robot: #e0552b; --robot-ink: #b4431f; --ros: #b06f0a; --wall: #e8eef3; --floor: #d9e1e8; --zebra: #eef1f4;
  --display: Archivo, "IBM Plex Sans", "Segoe UI", Arial, sans-serif;
  --body: "IBM Plex Sans", "Segoe UI", Arial, sans-serif;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #10151b; --surface: #19212a; --ink: #e7ecf1; --muted: #9ba7b3; --rule: #2d3844;
  --idea: #3fc3b8; --idea-tint: #163330; --idea-ink: #7fdcd3; --tool: #8ea6f4; --tool-tint: #1d2742;
  --robot: #ff7a4d; --robot-ink: #ff9b77; --ros: #f0aa3c; --wall: #1b242e; --floor: #222c37; --zebra: #161d25; color-scheme: dark; } }
:root[data-theme="dark"] {
  --bg: #10151b; --surface: #19212a; --ink: #e7ecf1; --muted: #9ba7b3; --rule: #2d3844;
  --idea: #3fc3b8; --idea-tint: #163330; --idea-ink: #7fdcd3; --tool: #8ea6f4; --tool-tint: #1d2742;
  --robot: #ff7a4d; --robot-ink: #ff9b77; --ros: #f0aa3c; --wall: #1b242e; --floor: #222c37; --zebra: #161d25; color-scheme: dark; }
body { background: var(--bg); color: var(--ink); font-family: var(--body); font-size: 15px; line-height: 1.5; margin: 0; }
.wrap { max-width: 1620px; margin: 0 auto; padding-block: 28px 48px;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); }
header { display: flex; flex-wrap: wrap; gap: 16px 32px; align-items: end; justify-content: space-between; margin-bottom: 18px; }
h1 { font-family: var(--display); font-weight: 800; font-size: clamp(28px, 3.6vw, 44px); line-height: 1.05; margin: 0 0 10px; letter-spacing: -0.015em; text-wrap: balance; }
.subtitle { font-family: var(--display); font-weight: 700; font-size: clamp(19px, 2vw, 25px); line-height: 1.2; color: var(--robot); margin: 0 0 6px; text-wrap: balance; }
.cite { font-size: 13.5px; font-style: italic; color: var(--muted); margin: 0 0 12px; }
.lede { margin: 0; max-width: 70ch; color: var(--muted); font-size: 16px; }
.node:focus-visible { outline: 3px solid var(--robot); outline-offset: 2px; }
.main { display: grid; grid-template-columns: minmax(0, 1fr) 370px; gap: 20px; align-items: start; }
@media (max-width: 1100px) { .main { grid-template-columns: minmax(0, 1fr); } .panel { position: static !important; } }
.scroll { overflow-x: auto; background: var(--surface); border: 1px solid var(--rule); border-radius: 14px; margin: 0; }
.scroll svg { display: block; width: 100%; min-width: 880px; height: auto; }
.panel { background: var(--surface); border: 1px solid var(--rule); border-radius: 14px; padding: 20px 22px; position: sticky; top: calc(env(safe-area-inset-top, 0px) + 12px); min-width: 0; }
.panel .kind { font: 600 12px var(--body); text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); margin: 0; }
.panel h2 { font-family: var(--display); font-size: 25px; margin: 2px 0 10px; line-height: 1.15; }
.panel h3 { font: 600 12px var(--body); text-transform: uppercase; letter-spacing: 0.07em; color: var(--muted); margin: 16px 0 5px; }
.panel p { margin: 0; }
.panel ul { margin: 0; padding-left: 18px; }
.panel li + li { margin-top: 2px; }
.chips { display: flex; flex-wrap: wrap; gap: 6px; list-style: none; padding: 0 !important; }
.chips li { margin: 0 !important; font: 500 13px var(--body); padding: 3px 9px; border-radius: 6px; background: var(--tool-tint); }
.real { border-left: 3px solid var(--robot); padding-left: 10px; }
.hint { font-size: 13px; color: var(--muted); margin-top: 18px !important; }
section.grid { margin-top: 20px; }
footer { margin-top: 18px; font-size: 13px; color: var(--muted); max-width: 90ch; }
/* Poster styling through tokens. */
text { font-family: var(--body); fill: var(--ink); }
.card { fill: var(--surface); stroke: var(--rule); stroke-width: 1.2; transition: stroke .15s, stroke-width .15s; }
.k-method { color: var(--idea); } .k-tool { color: var(--tool); }
.k-method .tint { fill: var(--idea-tint); } .k-tool .tint { fill: var(--tool-tint); }
.badge { fill: var(--idea); } .t-badge { fill: var(--surface); font-size: 11.5px; font-weight: 700; }
.chip { fill: var(--idea-tint); } .t-chip { font-size: 11px; font-weight: 600; fill: var(--idea-ink); }
.t-card { font-family: var(--display); font-size: 15px; font-weight: 700; } .t-tool { font-size: 14px; } .t-long { font-size: 12.5px; }
.t-tag { font-size: 11.5px; fill: var(--muted); }
.t-used { font-size: 11px; font-weight: 600; fill: var(--tool); }
.t-part { font-size: 11.5px; fill: var(--muted); }
.pin-dot { fill: var(--robot); stroke: var(--surface); stroke-width: 2; } .t-pin { fill: #fff; font-size: 13px; font-weight: 700; }
.r-idea { fill: var(--idea); } .r-tool { fill: var(--tool); } .r-robot { fill: var(--robot); }
.t-row { font-family: var(--display); font-size: 13px; font-weight: 800; letter-spacing: .14em; }
.r-idea-text { fill: var(--idea); } .r-tool-text { fill: var(--tool); } .r-robot-text { fill: var(--robot); }
.t-gap { font-size: 11px; font-style: italic; fill: var(--muted); }
.edge { fill: none; stroke-width: 1.8; stroke-linecap: round; transition: opacity .2s, stroke-width .2s; }
.e-idea { stroke: var(--idea); opacity: .4; } .e-tool { stroke: var(--tool); opacity: .4; }
.e-use { stroke-width: 1.4; stroke-dasharray: 1.5 4; opacity: .55; } svg.focus .edge.key-line { opacity: .8; }
.t-topic { font-family: "IBM Plex Mono", Consolas, monospace; font-size: 12px; font-weight: 600; fill: var(--ros); }
.flow-out { animation: topic-out 1.1s linear infinite; } .flow-in { animation: topic-in 1.1s linear infinite; }
@keyframes topic-out { to { stroke-dashoffset: -14; } } @keyframes topic-in { to { stroke-dashoffset: 14; } }
.scene-wall { fill: var(--wall); } .scene-floor { fill: var(--floor); }
.t-scene { font-size: 11.5px; fill: var(--muted); font-style: italic; }
.t-ros { font-size: 12px; font-weight: 700; fill: var(--ros); }
.t-scene-tag { font-size: 11px; font-weight: 700; letter-spacing: .1em; fill: var(--muted); }
.ic { fill: none; stroke: currentColor; stroke-width: 2.6; stroke-linecap: round; stroke-linejoin: round; }
.ic-thin { fill: none; stroke: currentColor; stroke-width: 1.3; opacity: .6; }
.ic-fill { fill: currentColor; } .ic-soft { fill: currentColor; opacity: .22; }
.ic-dot { fill: var(--surface); stroke: currentColor; stroke-width: 2.2; }
.ic-dash { stroke-dasharray: 4 3.5; }
.ic-acc { fill: none; stroke: var(--robot); stroke-width: 2.6; stroke-linecap: round; stroke-linejoin: round; }
.ic-acc-fill { fill: var(--robot); }
.ax-x { stroke: #d8402f; } .ax-xf { fill: #d8402f; } .ax-y { stroke: #23974a; } .ax-yf { fill: #23974a; }
.ax-z { stroke: #3a6fe0; } .ax-zf { fill: #3a6fe0; }
.sh-red { fill: #d23b36; } .sh-blue { fill: #3b62d6; } .sh-yellow { fill: #e2bb22; }
.grid-band { fill: transparent; } .grid-row:nth-of-type(even) .grid-band { fill: var(--zebra); }
.t-grid-title { font-family: var(--display); font-size: 17px; font-weight: 700; }
.t-grid-head { font-size: 11.5px; font-weight: 600; } .t-grid-label { font-size: 12.5px; font-weight: 600; }
.dot { fill: var(--tool); } .ring { fill: var(--surface); stroke: var(--tool); stroke-width: 1.6; }
/* Selection: dim what is unrelated, outline what is selected. */
.node { cursor: pointer; transition: opacity .2s; }
.node:hover .card { stroke: var(--ink); }
svg.focus .k-method:not(.on), svg.focus .k-tool:not(.on), svg.focus .k-part:not(.on) { opacity: .22; }
svg.focus .k-part:not(.on):not(.pin) { opacity: .45; }
svg.focus .edge { opacity: .08; }
svg.focus .edge.on { opacity: 1; stroke-width: 2.8; } svg.focus .edge.e-use.on { stroke-width: 2.2; }
svg.focus .node.selected .card { stroke: var(--robot); stroke-width: 3; }
svg.focus .pin.on .pin-dot { stroke: var(--robot); stroke-width: 4; }
.grid-row.selected .grid-band { fill: var(--tool-tint); }
@media (prefers-reduced-motion: reduce) { * { transition: none !important; animation: none !important; } }
__SCENE_CSS__
</style>
</head>
<body>
<div class="wrap">
<header>
  <div>
    <h1>Line upon Line</h1>
    <p class="subtitle">From rotation matrices to a robot that sees, decides, and acts.</p>
    <p class="cite">“Line upon line, precept upon precept.” 2 Nephi 28:30</p>
    <p class="lede">The course content builds up to one final project: a 4-joint simulated robotic arm that sorts parts off a moving conveyor using camera data and computer vision techniques. Each idea you learn is built with a tool, and each tool works with a part of the robot. Click any item to follow its path and learn more about the topic or tool.</p>
  </div>
</header>
<div class="main">
  <figure class="scroll">
    <svg id="poster" viewBox="0 0 __WIDTH__ __POSTER_H__" role="img" aria-label="Course ideas, the tools that build them, and the robot hardware each tool works with">__POSTER__</svg>
  </figure>
  <aside class="panel" id="panel" aria-live="polite"></aside>
</div>
<section class="grid" aria-label="Where each tool appears in the course">
  <div class="scroll">
    <svg id="grid" viewBox="0 0 __WIDTH__ __GRID_H__" role="img" aria-label="Which assignments use each tool">__GRID__</svg>
  </div>
</section>
<footer>Course draft. Generated by <code>docs/figures/robot_stack.py</code>, which also writes the static <code>robot_stack.svg</code> for slides and handouts.</footer>
</div>
<script type="application/json" id="detail-data">__DATA__</script>
<script>
(function () {
  var data = JSON.parse(document.getElementById("detail-data").textContent);
  var poster = document.getElementById("poster");
  var grid = document.getElementById("grid");
  var panel = document.getElementById("panel");
  var current = "vision";

  function el(tag, text, cls) {
    var node = document.createElement(tag);
    if (text) node.textContent = text;
    if (cls) node.className = cls;
    return node;
  }
  function list(items, cls) {
    var ul = el("ul", null, cls);
    items.forEach(function (item) { ul.appendChild(el("li", item)); });
    return ul;
  }
  function section(title, body) {
    panel.appendChild(el("h3", title));
    panel.appendChild(body);
  }

  function render(id) {
    var d = data[id];
    if (!d) return;
    current = id;
    panel.replaceChildren();
    panel.appendChild(el("p", d.kind, "kind"));
    panel.appendChild(el("h2", d.name));
    if (d.what) panel.appendChild(el("p", d.what));
    (d.groups || []).forEach(function (g) { if (g[1].length) section(g[0], list(g[1], "chips")); });
    if (d.project) section("In the project", el("p", d.project));
    if (d.course) section("In this course (simulated)", el("p", d.course));
    if (d.real) section("On a real robot", el("p", d.real, "real"));
    if (d.reach) section("Reach for it when", list(d.reach));
    if (d.beyond) section("Beyond this course", list(d.beyond));
    panel.appendChild(el("p", "Click any idea, tool, or part of the robot, or a row in the grid below.", "hint"));

    var on = {};
    d.on.forEach(function (k) { on[k] = true; });
    poster.classList.add("focus");
    poster.querySelectorAll(".node").forEach(function (n) {
      var key = n.getAttribute("data-id");
      n.classList.toggle("on", !!on[key]);
      n.classList.toggle("selected", key === id);
    });
    poster.querySelectorAll("[data-ends]").forEach(function (e) {
      var ends = e.getAttribute("data-ends").split(" ");
      e.classList.toggle("on", !!(on[ends[0]] && on[ends[1]]));
    });
    grid.querySelectorAll(".grid-row").forEach(function (r) {
      r.classList.toggle("selected", r.getAttribute("data-id") === id);
    });
  }

  function choose(event) {
    var node = event.target.closest(".node[data-id]");
    if (node && data[node.getAttribute("data-id")]) render(node.getAttribute("data-id"));
  }
  [poster, grid].forEach(function (svg) {
    svg.addEventListener("click", choose);
    svg.addEventListener("keydown", function (event) {
      if (event.key === "Enter" || event.key === " ") { event.preventDefault(); choose(event); }
    });
  });

  render(current);
})();
</script>
</body>
</html>
"""


def write_html():
    grid, grid_height = draw_grid()
    page = (PAGE.replace("__SCENE_CSS__", SCENE_CSS)
            .replace("__WIDTH__", str(WIDTH))
            .replace("__POSTER_H__", str(POSTER_H))
            .replace("__GRID_H__", str(grid_height))
            .replace("__POSTER__", "".join(draw_poster()))
            .replace("__GRID__", "".join(grid))
            .replace("__DATA__", json.dumps(detail_data(), ensure_ascii=False).replace("</", "<\\/")))
    (HERE / "robot_stack.html").write_text(page, encoding="utf-8")


if __name__ == "__main__":
    write_static()
    write_html()
    print("wrote", HERE / "robot_stack.svg", "and", HERE / "robot_stack.html")
