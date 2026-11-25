# Introduction to Robotics: instructor source

A 14-week Mechanical Engineering course connecting robot geometry, planning,
vision, feedback, and learning. Students have prior linear algebra and Python
but may be new to classes and robotics. This faculty repository contains
completed masters and prototypes; generate a reviewed student copy rather
than distributing this working tree.

## Faculty planning: start here

1. **[TASKS.md](TASKS.md)**: decisions needed from the instructor, the review
   queue of draft material, and open work.
2. **[Planning and design index](docs/design/README.md)**: what every other
   planning document is for, plus decisions already made and their rationale.
3. [Course roadmap](COURSE_ROADMAP.md): goals, scope, and the weekly sequence.

Student-facing entry points: [setup](docs/setup.md), the
[quick start](docs/quick_start.md), [troubleshooting](docs/troubleshooting.md),
and the [student homework guide](STUDENT_GUIDE.md).

## Start RViz

Start Docker Desktop (Windows/macOS), or the Linux Docker engine. From this
folder in a **host terminal**:

```text
docker compose build
docker compose up -d
```

**Open your browser yourself** and visit:

**<http://localhost:6080/vnc.html?autoconnect=1&resize=scale>**

This local Linux desktop starts empty, with a taskbar; the container starts
no ROS nodes (instructor decision, Nov 24). Docker Desktop's dashboard is a
different window. Build the ROS packages and start the demo in a container
shell (`docker compose exec course bash`):

```bash
cd /workspace/student_ws/ros2_ws
colcon build
source install/setup.bash
ros2 launch r2d2_demo view_r2d2.launch.py
```

Use Move Camera and drag to orbit; scroll to zoom. Hidden windows are on the
taskbar.

Read [the setup guide](docs/setup.md), including its distinction between a
host terminal and a ROS-enabled container shell. See platform details for
[Windows](docs/windows.md) and [macOS](docs/macos.md), and the
[troubleshooting](docs/troubleshooting.md) page.

To stop, run this in a **host terminal**:

```text
docker compose down
```

Then close the browser tab and optionally quit Docker Desktop. Closing only
the browser tab leaves the container running. Source files remain on disk.
After a Docker update/reboot, restart the engine and run `docker compose up -d`.

## HW01 publisher mode

The student writes a short ROS 2 publisher that first holds a pose and then
animates joints using a timer. In one container shell, start RViz and
`robot_state_publisher` without the slider publisher:

```bash
ros2 launch r2d2_demo view_r2d2.launch.py use_joint_gui:=false
```

In a second container shell:

```bash
cd /workspace
python3 homework/hw01/joint_publisher.py
```

**Here that file is the completed instructor master.** The release generator
removes its two answer blocks. Follow the [HW01 guide](homework/hw01/README.md)
when preparing student directions. Returning to `docker compose up -d
--force-recreate` restores the sliders. Refresh the browser after recreation.

## Rotation, transform, FK, and planar-Jacobian homeworks

`src/intro_robotics/` keeps `SerialArm` and `fk`, introduces explicit `Joint`
geometry, and provides a checked `jacob_planar` returning three task rows.
FK and visualization support spatial arms; the planar Jacobian deliberately
rejects spatial mechanisms. A supplied DH adapter demonstrates future
graduate-course reuse without making DH an undergraduate topic.

The first renderer uses Matplotlib lines, joint markers, physical axes, and
frames. It does not depend on the old DH-specific mesh renderer or a ROS
runtime. The cumulative HW02--HW05 drafts assign nine short mathematical
methods; input checks, physical joint modeling, and drawing are supplied.
The release generator removes the mathematical answer bodies while retaining
their guidance and homework-labeled errors. The DH adapter and project
prototypes stay faculty-only. These boundaries await faculty review.

Students run HW02--HW05 natively in a `.venv` (`pip install -e
".[visualization]"`; see [setup](docs/setup.md#python-on-your-own-computer-hw02--hw05)),
so the viewers open as ordinary windows. The ROS problems and everything from
HW06 on run in the container, which also runs these commands from
`/workspace` as a fallback. From the repository root with `.venv` activated:

```text
python -m homework.hw02.hw02_rotations --show
python -m homework.hw03.hw03_transforms --show
python -m homework.hw04.hw04_fk --show
python -m homework.hw04.play_arm
python -m homework.hw05.hw05_planar_jacobian --show
```

The completed faculty methods make those demonstrations run here. Students
complete each stage before its scene can run. See the
[student guide](STUDENT_GUIDE.md) for cumulative dependencies and save-only use.

For faculty Python development, create a virtual environment and run:

```text
python -m pip install -e ".[visualization]"
python -m unittest discover -s tests/instructor -v
python examples/arm_viewer.py --model planar
```

Choose `--model spatial` or `--model dh` for the other examples. See the
[prototype guide](docs/design/arm-prototype.md) for frames, checks, and limits.

## Conveyor project

The project simulator, scenarios, lockstep runner, and live ROS graph are
described in the [student project guide](homework/project/README.md) and the
[faculty specification](instructor/PROJECT_SPEC_DRAFT.md). The faculty
reference controller and oracle are excluded from the student release.

## Current validation

The original demo was observed on Apple Silicon (`linux/arm64`) in October
2026. On November 12, 2026 it built and launched on Windows/WSL 2
(`linux/amd64`), including all sliders and camera controls. RViz reported
OpenGL 4.5 with software rendering, and ROS joint states matched TF.
The [validation record](docs/design/validation.md#windows-host-observations)
identifies observed versions and limits.
On November 13 the rebuilt image also passed the foundation activities,
frame updates, and a real Tk slider/event-loop check. This automated check
does not establish hands-on usability on other platforms. See the
[validation record](docs/design/validation.md) and remaining tasks.

## Student release

```text
python -m release_tools --dry-run
```

The preview copies an explicit HW01--HW05 allowlist, strips answers only in that
copy, validates Python syntax, reports input hashes/source revision, then
discards it. Real review copies require clean, committed source. Publication
is a separate faculty action. Never strip the instructor working tree.

## Repository layout

```text
docker/                 Linux ROS 2/browser-desktop startup
docs/                   Setup, design rationale, faculty LaTeX sources
homework/hw01--hw05/    Activities, provided models, and marked publisher master
src/intro_robotics/     Marked math masters and supplied geometry/drawing
examples/              Faculty prototype demonstrations
tests/instructor/      Numerical, release, and maintenance checks
tests/public/          Limited student checks by assignment
instructor/            Migration records and improvement lists
release_tools/         Allowlisted, separate student-copy generation
student_ws/            Persistent standalone Python and ROS workspaces
```
