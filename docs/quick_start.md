# Quick start: every work session

The commands you use every session, once [setup](setup.md) is complete. A
**host terminal** is a VS Code terminal on your own computer, in the course
folder. A **container shell** is the Linux terminal inside the course
container ([two places to run commands](setup.md#two-places-to-run-commands)).

## ROS work (HW01, HW03 problem 4, HW04 problem 5, and everything from HW06 on)

| Step | Command | Type it in |
| --- | --- | --- |
| 1. Start Docker | Open the Docker Desktop app and wait until it is running | (Windows/macOS) |
| 2. Start the container | `docker compose up -d` | Host terminal |
| 3. Open the desktop | <http://localhost:6080/vnc.html?autoconnect=1&resize=scale> | Your web browser |
| 4. Open a container shell | `docker compose exec course bash` | Host terminal |
| 5. Run your work | for example `ros2 launch r2d2_demo view_r2d2.launch.py` or the homework's command | Container shell |
| 6. Finish | Ctrl+C to stop programs, `exit`, then `docker compose down` | Container shell, then host terminal |

Need a second program running at the same time? Open another VS Code terminal
(the **+** in the terminal panel) and repeat step 4 there. A window hidden
behind another one is on the browser desktop's taskbar. If you changed
anything inside a ROS package, rebuild it in a container shell:
`cd /workspace/student_ws/ros2_ws`, `colcon build`, `source install/setup.bash`.

## Python on your own computer (HW02--HW05)

| Step | Command | Type it in |
| --- | --- | --- |
| 1. Activate Python | automatic in a new VS Code terminal; otherwise `.\.venv\Scripts\Activate.ps1` (Windows) or `source .venv/bin/activate` (macOS/Linux) | Host terminal |
| 2. Run an activity | for example `python -m homework.hw02.hw02_rotations --show` | Host terminal, prompt starts with `(.venv)` |
| 3. Run the public checks | for example `python -m unittest discover -s tests/public -p "test_hw02_*.py" -v` | Host terminal |

Docker does not need to be running for these.

Something not working? See [troubleshooting](troubleshooting.md).
