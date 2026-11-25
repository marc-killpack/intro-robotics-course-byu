# Troubleshooting

Find your symptom below. If nothing here helps, send the instructor or TA
your operating system, the command you ran, and the full error text (a
screenshot of the terminal is fine). Terms such as *host terminal* and
*container shell* are explained in [setup](setup.md#two-places-to-run-commands).

## Docker

### `docker version` shows only a Client section

The Docker engine is not running. Start Docker Desktop, wait until it reports
that the engine is running (this can take a minute after a reboot), and try
again. [Setup](setup.md#check-that-docker-is-running) shows what the full
output looks like. On Windows, also check `wsl --status` (see
[Windows setup](windows.md)).

### The browser page does not load or stays blank

1. Check that the container is running, in a host terminal:

   ```text
   docker compose ps -a
   ```

   The `course` line should say `Up`. If it says `Exited`, or there is no
   line, run `docker compose up -d`.
2. Look at the container's messages:

   ```text
   docker compose logs course
   ```

   When startup is complete, the last lines include
   `Course desktop ready (screen 1280x800).` If that line is missing, the
   container is still starting (wait a few seconds and run the command
   again) or an error is shown just above where it would be.
3. Refresh the browser page.

If you run `docker compose logs -f course` instead, the messages keep
streaming; press Ctrl+C to stop following them. This does not stop the
container.

### Port 6080 is already in use

`docker compose up -d` reports that port 6080 is already allocated: another
program, or an older container, is using it. Run `docker compose down` and
try again. If it still fails, change the left number in the `ports` line of
`compose.yaml` (for example `"127.0.0.1:6081:6080"`) and use that number in
the browser address (`localhost:6081`).

### Something stopped working after Docker Desktop updated or the computer restarted

Start Docker Desktop and wait for the engine. Then run `docker compose up -d`
again in a host terminal and refresh the browser page.

### Windows: the container exits with `$'\r': command not found`

Windows and Linux mark the end of a line in a text file differently (Windows
uses two characters, CRLF; Linux uses one, LF). The startup script
`docker/start-gui.sh` must keep Linux line endings or the container cannot
run it. The repository is set up to keep them, but an editor or an older copy
can change them. Open `docker/start-gui.sh` in VS Code, click **CRLF** in the
blue status bar at the bottom right, choose **LF**, save, then run
`docker compose build` and `docker compose up -d --force-recreate`.

### Mac: the image reports `linux/amd64` on Apple Silicon

The image should be `linux/arm64` on an Apple Silicon Mac; `amd64` runs in
slow emulation. Make sure you installed Docker Desktop for Apple Silicon, then
rebuild with `docker compose build` and ask the instructor if it persists.

## Browser desktop

### A window is hidden, minimized, or missing

Click the window's name on the taskbar at the bottom of the browser desktop.
New windows often open behind RViz. If a window was closed, start its program
again (for the robot demo, press Ctrl+C in the shell that ran `ros2 launch`,
then run the same command again).

### A window responds slowly

Everything on the browser desktop is drawn by your computer's processor, not
its graphics card, so RViz is slower than a normal app, especially while it
starts or while many windows are open. Give it a few seconds, close windows
you no longer need, and try a smaller screen size (next section).

### Screen size and speed

The browser desktop is 1280 by 800 pixels by default, scaled to fit your
browser window. A smaller desktop draws faster; a larger one looks sharper on
a big or high-resolution monitor. To change it, create a file named `.env`
(nothing before the dot) in the course folder, next to `compose.yaml`,
containing one line:

```text
COURSE_SCREEN=1024x640
```

Then, in a host terminal, recreate the container and refresh the browser page:

```text
docker compose up -d --force-recreate
```

`docker compose logs course` reports the size in use. Try `1024x640` for
speed or `1600x1000` for sharpness; delete `.env` to return to the default.
To compare, orbit the robot in RViz with each size while watching the
container's processor use in a second host terminal with `docker stats`
(Ctrl+C to stop); a lower `CPU %` while you drag means less work.

Other options in the browser:

- Press F11 (or use the browser's full-screen mode) to give the desktop more
  room.
- noVNC's side menu (the small tab on the left edge of the page) has a
  settings gear. **Scaling mode: Local scaling** fits the desktop to the
  window (the default from the bookmark); **None** shows it pixel for pixel,
  sharper but with scroll bars when it does not fit.

## ROS

### `Package 'r2d2_demo' not found`

The course packages are not built yet, or this shell does not know about
them. In the container shell:

```bash
cd /workspace/student_ws/ros2_ws
colcon build
source install/setup.bash
```

Container shells opened after a successful build find the packages
automatically.

### `build`, `install`, and `log` folders appeared in the wrong place

`colcon build` creates these folders in whatever directory you run it from.
If you ran it somewhere other than `/workspace/student_ws/ros2_ws` (for
example `/workspace`), delete the stray folders there and build again from
the right place. The ones inside `student_ws/ros2_ws` are correct; Git ignores
them.

### `colcon build` prints clock skew warnings

On Windows and macOS the mounted folder's file times can disagree slightly
with the container's clock. Warnings such as `Clock skew detected` are
harmless if the build finishes with `Summary: ... packages finished`.

### `ros2 topic echo` prints nothing

A topic only has data while some node publishes it. Check what is running
with `ros2 topic info /joint_states --verbose` (it lists publishers and
subscribers). For example, if the robot demo's slider window was closed, or
your own publisher is not running, nothing publishes `/joint_states`. Press
Ctrl+C to stop waiting.

### The robot jumps between two poses

Two nodes are publishing `/joint_states` at once, for example the slider
window and your HW01 publisher. `ros2 topic info /joint_states --verbose`
shows the publisher count. For HW01, launch the demo with
`use_joint_gui:=false` so only your node publishes.

### `Could not connect to display` or a window never appears

Run the command in a container shell (not a host terminal), and make sure the
browser desktop page is open. Container shells are already set to draw on the
browser desktop.

## Python on your own computer

### Windows: `py install` says `can't open file ...\install`

Your `py` is an older Python launcher, which does not have the `install` (or
`list`) command and treats the word as a file name. You do not need it:
follow [Install Python](setup.md#install-python-once), which starts by
checking whether Python 3.13 is already installed with
`py -V:3.13 --version`.

### PowerShell says running scripts is disabled

Windows blocks the `.venv` activation script by default. Run this once, then
activate again:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### `NotImplementedError` when running a homework activity

This is expected until you complete the function the message names; the
setup is working. Earlier homework functions must be complete before later
activities that use them can run.

### `No module named intro_robotics` or `No module named homework`

Either `.venv` is not active (the prompt does not start with `(.venv)`), or
you are not in the course folder (the one containing `pyproject.toml`).
Activate `.venv`, change to the course folder, and run the command again.

## How the browser desktop works

For the curious: the container runs a virtual display drawn in software
(Mesa), and a small web server (noVNC) shows that display in your browser.
It is only reachable from your own computer (`localhost`), not from the
network.
