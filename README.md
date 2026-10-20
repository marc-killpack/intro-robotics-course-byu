# Introduction to Robotics

Starter repository for the Mechanical Engineering introduction to robotics
course. The initial goal is a repeatable ROS 2 environment with RViz on
Windows, macOS, and Linux. Course lessons and simulation choices will be added
after the environment is established.

The [course requirements and roadmap](COURSE_ROADMAP.md) records the intended
finished course, open decisions, and a research brief for finding comparable
teaching materials.

## Course environment

- Ubuntu 24.04 and ROS 2 Jazzy in Docker
- Docker Compose is the base workflow; VS Code dev containers can be layered
  on top later without changing the image
- `student_ws/ros2_ws/` for ROS 2 packages and `student_ws/python/` for
  standalone Python work
- A small R2D2-like robot, joint sliders, and RViz open in a local browser
  page using software rendering; no host X11 server is required

The reference repositories in the development workspace informed this layout:
the rover project for ROS 2/Docker practices, the Baxter lab for GUI and
platform troubleshooting, and the robotics homework repository for separating
student materials from faculty solutions and preparing reviewed releases.

## Start here

Install Docker Desktop on Windows/macOS, or Docker Engine with the Compose
plugin on Linux. Apple Silicon setup is detailed in [docs/macos.md](docs/macos.md),
which also has a starter validation section for Intel Macs. From this
repository's root directory, build and start the image:

```bash
docker compose build
docker compose up -d
```

Open <http://localhost:6080/vnc.html?autoconnect=1&resize=scale> to see the
robot in RViz and move its three joint sliders. This is the first student
[installation exercise](student_ws/ros2_ws/src/r2d2_demo/README.md). See
[docs/gui.md](docs/gui.md) for display details. Open a ROS-enabled shell:

```bash
docker compose exec course bash
```

Stop the environment with:

```bash
docker compose down
```

Inside the shell, build and source the student ROS workspace with:

```bash
cd /workspace/student_ws/ros2_ws
colcon build
source install/setup.bash
```

The Python workspace is available under `/workspace/student_ws/python`.

## Apple Silicon Mac setup

These steps are for any M-series Mac. Install and start **Docker Desktop for
Apple Silicon**, then open Terminal. `uname -m` should print `arm64`, and
`docker info --format '{{.OSType}}/{{.Architecture}}'` should report a Linux
ARM64 engine. From this folder, run:

```bash
docker compose build
docker compose up -d
```

Open <http://localhost:6080/vnc.html?autoconnect=1&resize=scale> in your
browser. RViz and the robot's slider window should appear there. Use `docker compose exec course bash` for
student code and `docker compose down` when finished. The image uses a native
ARM64 ROS 2 base and a software-rendered browser desktop; XQuartz is not
required. See [the full Mac guide](docs/macos.md) for first-run checks and
troubleshooting.

### Intel Mac (to validate)

An Intel Mac should use the same Compose commands with a `linux/amd64` image.
This has not yet been checked on Intel hardware. The [Intel Mac validation
section](docs/macos.md#intel-mac-validation-to-do) lists what to record and
where to add any platform-specific directions.

## Repository layout

```text
docker/                 Container image definition
docs/                   Platform setup and maintenance notes
instructor/             Faculty-only material (not for student releases)
release_tools/           Student publication workflow notes
student_ws/python/       Standalone Python exercises
student_ws/ros2_ws/src/  Student ROS 2 packages, starting with r2d2_demo
```

## Course content roadmap

The course repository is intended to grow in stages: homogeneous transforms;
forward kinematics and DH parameters; 2.5D velocity kinematics and Jacobians;
path planning for arms and mobile bases; computer vision and visual servoing;
then learned vision models and reinforcement-learning policies. Simulator
selection (Gazebo, MuJoCo, or another ROS 2-compatible option) remains open
until the baseline workflow has been exercised across student platforms.

## Instructor release workflow

Keep canonical instructor material in the maintained repository. Before a
student handout/repository is published, create a reviewed student copy or
release from a clean revision and inspect its contents. Do not put private
solutions in student-facing workspaces. A later release script should use an
explicit allowlist and operate on a copy, following the safer pattern used by
the reference robotics homework repository.

## Current status

The Apple Silicon container builds as `linux/arm64`. On the instructor Mac,
RViz started with OpenGL 4.5 and the browser desktop served successfully.
The R2D2-like demo now starts on the instructor Mac: its head slider changed
`/joint_states` and the RViz picture. Classroom responsiveness and other host
platforms still need a hands-on check.
Intel Mac, Windows, and Linux results should be recorded after tests on
representative machines.

