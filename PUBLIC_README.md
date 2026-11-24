# Introduction to Robotics

Start with **[setup, browser access, and shutdown](docs/setup.md)**, then
complete **[HW01: a ROS 2 joint-state publisher](homework/hw01/README.md)**
using the assignment handout supplied by your instructor.

Continue with [the cumulative Python workflow](STUDENT_GUIDE.md) and the
provided activity guides for [HW02](homework/hw02/README.md),
[HW03](homework/hw03/README.md), [HW04](homework/hw04/README.md), and
[HW05](homework/hw05/README.md). Complete assignments in order; later methods
intentionally remain labeled stubs until you implement them. HW02--HW05 run
Python on your own computer; their ROS problems and later work run in the
container. See [two places to run commands](docs/setup.md#two-places-to-run-commands).

This repository uses ROS 2 Jazzy on Ubuntu 24.04 inside Docker. Start Docker
Desktop on Windows/macOS, or your Docker engine on Linux. From this folder
in your computer's terminal:

```text
docker compose build
docker compose up -d
```

Then open your usual browser and visit:

**<http://localhost:6080/vnc.html?autoconnect=1&resize=scale>**

The page displays RViz and joint sliders; Docker Desktop itself is not that
display. Wait for the first package build. Sliders may open behind RViz:
move or minimize its window to reveal them. For a ROS-enabled container
shell, run `docker compose exec course bash` from a host terminal.

To stop, run `docker compose down` in a host terminal. Then you may close
the browser tab and quit Docker Desktop. Closing the tab alone does not stop
the course container. Your source files remain in the repository folder.

Use `student_ws/python/` for later standalone Python work and
`student_ws/ros2_ws/src/` for ROS packages. HW01 starts with one standalone
ROS-aware Python script to keep the first exercise small.

Follow [the AI tutoring policy](AI_TUTORING_GUIDE.md), keep your code readable,
and disclose AI use as requested. This release covers HW01--HW05. Planning,
vision, learning, and project exercises will be supplied after their design
and review are complete.
