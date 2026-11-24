# Start, view, and stop the course environment

## Install and open the repository

Use the **student repository link supplied by the instructor**; the faculty
source contains answers and is not the student starting point. Open the
cloned folder in VS Code or your preferred Python editor. Terminal commands
below are run in the folder containing `compose.yaml`.

- Windows: install/start Docker Desktop using WSL 2 and Linux containers.
  See [Windows setup](windows.md).
- Apple Silicon or Intel Mac: install/start the matching Docker Desktop.
  See [Mac setup](macos.md). Intel Mac validation is still pending.
- Linux: install Docker Engine and its Compose plugin using
  [Docker's installation guide](https://docs.docker.com/engine/install/).
  This host workflow has not yet been validated for this course.

You will also install Python on your own computer before HW02; see
[Python on your own computer](#python-on-your-own-computer-hw02--hw05).

Confirm that `docker version` reports **both a client and server**, and
`docker compose version` reports Compose. A client-only result means the
engine is unavailable; start Docker Desktop and wait for it to be ready.

## Start the Linux desktop

In a **host terminal** (PowerShell on Windows; Terminal on macOS/Linux):

```text
docker compose build
docker compose up -d
```

The first build downloads ROS 2 and graphics dependencies. Later starts reuse
the image. The course source folder is mounted into `/workspace`, so source
edits persist on your computer. The first start also builds the robot package.

## Open the web page yourself

Open your usual browser on this same computer and visit:

**<http://localhost:6080/vnc.html?autoconnect=1&resize=scale>**

Bookmark this address. Docker Desktop's dashboard does not display RViz;
the URL opens a separate local Linux desktop containing RViz and joint
sliders. No automatic browser opening is required. Wait for the robot to
appear. The first package build took about 39 seconds on the tested Windows
machine; this is an observation, not a startup-time guarantee.

If only RViz is visible, move or minimize its Linux window: the **Joint State
Publisher** window can start behind it. Try all three sliders. Select
**Move Camera** and drag in the dark 3D view to orbit; scroll to zoom.

If the page is unavailable or the robot does not appear:

```text
docker compose ps -a
docker compose logs -f course
```

Look for package-build completion and the RViz OpenGL startup message. Ctrl+C
stops following logs without stopping the container. Check that another
program is not already using port 6080. After a Docker update/reboot, start
the engine, run `docker compose up -d`, and refresh the page.

## Two places to run commands

You type commands in one of two places. Both use the same files: Docker
mounts this repository folder into the container as `/workspace`, so a file
you save in your editor is the file the container runs. Nothing is copied,
and ordinary edits never need a rebuild.

| | Host terminal | Container shell |
| --- | --- | --- |
| What it is | A terminal on your own computer (PowerShell on Windows, Terminal on macOS/Linux, or VS Code's terminal), opened in the repository folder | A Linux shell inside the course container, opened from a host terminal with `docker compose exec course bash` |
| Prompt starts with | `(.venv) PS C:\...>` on Windows or `(.venv) you@laptop ...` on macOS/Linux, once `.venv` is activated | `student@` and ends with `:/workspace$` |
| Use it for | `docker compose` commands; HW02--HW05 Python activities, slider viewers, and public checks | Anything with ROS (`ros2`, launch files, TF, URDF, RViz): HW01, HW03 problem 4, HW04 problem 5; and all work from HW06 on |
| Windows open on | Your own desktop | The [browser desktop](#open-the-web-page-yourself) |

**Rule of thumb:** if a step mentions ROS, TF, URDF, or RViz, or starts with
`ros2`, use the container shell. Otherwise, during HW02--HW05, use a host
terminal with `.venv` activated. From HW06 on, use the container shell.

To get the ROS-enabled **Linux shell inside the container**, run this in a
host terminal while the container is running (`docker compose up -d`):

```text
docker compose exec course bash
```

Inside that shell, `/workspace` is this repository. For example:

```bash
cd /workspace
ros2 topic list
ros2 topic echo /joint_states --once
```

Use `exit` to leave that shell; the background course container keeps running.
For [HW01](../homework/hw01/README.md), switch to its publisher mode before
running the student node. Keep the GUI slider node disabled in that mode.

## Python on your own computer (HW02--HW05)

<!-- FACULTY REVIEW (Nov 23, 2026): draft section, TASKS.md R12. Remove this
comment after review; it is copied into the student release. -->

HW02--HW05 are plain Python: rotation matrices, transforms, forward
kinematics, and planar Jacobians, with a 3D arm viewer for checking them.
Run them on your own computer so the viewer opens as a normal window. Their
ROS problems (HW03 problem 4, HW04 problem 5) still run in the container,
using the same files.

### Install Python (once)

Use **Python 3.12 or 3.13**. If you have neither, install 3.13 from
[python.org](https://www.python.org/downloads/). Newer versions work on
Windows, Linux, and recent Macs, but the 3D viewer's Qt package does not yet
support them on every older Mac (Python 3.14 needs macOS 13 or newer, and
3.15 needs macOS 14 or newer), so 3.13 is the safe choice.

- **Windows:** `py -0` lists the versions you have. The python.org installer
  includes the `py` launcher used below.
- **macOS:** after the python.org installer, `python3.13 --version` should work.
- **Linux (Ubuntu 24.04):** the system Python 3.12 is fine. Also run
  `sudo apt install python3-venv libxcb-cursor0`; Qt needs the second
  package to open windows.

### Create the course environment (once)

In a host terminal in the repository folder. **Windows (PowerShell):**

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[visualization]"
```

**macOS** (on Linux, use `python3` in the first line):

```sh
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[visualization]"
```

`.venv` is a folder holding this course's Python packages (roughly 100--150
MB of downloads), separate from anything else on your computer. Git ignores
it, and the container uses its own copy of these packages. `-e` (editable) means Python runs your files in
`src/intro_robotics/` directly, so you never reinstall after editing them.

If PowerShell says running scripts is disabled, run
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, then activate
again.

### Check the viewer (once)

With `.venv` activated:

```text
python -c "import numpy as np; from intro_robotics.visualization_3d import VizScene; s = VizScene(); s.add_frame(np.eye(4), label='world'); s.hold()"
```

A window with a grid and red/green/blue axes should open. Drag to orbit and
scroll to zoom; close the window to return to the terminal. This works before
you have implemented anything.

### Each work session

1. Open a host terminal in the repository folder.
2. Activate the environment: `.\.venv\Scripts\Activate.ps1` on Windows, or
   `source .venv/bin/activate` on macOS/Linux. The prompt now starts with
   `(.venv)`.
3. Run activities and checks from the repository folder, for example:

   ```text
   python -m homework.hw02.hw02_rotations --show
   python -m unittest discover -s tests/public -p "test_hw02_*.py" -v
   ```

Docker does not need to be running for these; it does for the ROS problems.
In VS Code, choose **Python: Select Interpreter** and pick `.venv`; new VS
Code terminals then activate it automatically.

**If this setup does not work on your computer,** the container has
everything: run the same commands in a container shell from `/workspace`,
and the windows open on the browser desktop instead. Tell the instructor or
TA your operating system, Python version, and the error so it can be fixed.

## Python in the container (HW06 onward)

From HW06 on, run Python in a container shell. The image adds OpenCV, SciPy,
PyTorch, and the reinforcement-learning packages at tested versions, and its
windows open on the browser desktop. Follow
[the cumulative Python guide](../STUDENT_GUIDE.md) and your homework handout.

Inside the container, check the vision installation with:

```bash
python -c "import cv2; print(cv2.__version__)"
```

To check an OpenCV window, run this in the container shell while the browser
desktop is open:

```bash
python - <<'PY'
import cv2
import numpy as np

image = np.zeros((200, 300, 3), dtype=np.uint8)
image[:] = (0, 180, 0)
cv2.imshow("OpenCV test", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
PY
```

Click the green window and press a key to close it. If it is hidden, move or
minimize RViz. Matplotlib is also available for plots and side-by-side image
comparisons. OpenCV reads color files as BGR, so convert to RGB before
displaying them with Matplotlib.

If you received Dockerfile or startup-script updates after building an older
image, run this in a **host terminal**:

```text
docker compose build
docker compose up -d --force-recreate
docker compose exec course bash
```

In the container, `--show` opens figures on the browser desktop (move or
minimize RViz if needed), and `--save tmp/name.png` saves a figure without
opening a window. Run modules from `/workspace` so the provided homework
support imports correctly.

## Stop when finished

In a **host terminal**:

```text
docker compose down
```

Then close the browser tab and, if desired, quit Docker Desktop. Closing
only the browser tab leaves the container running. `down` does not delete
your source folder or cached image. Next time, start Docker Desktop, run
`docker compose up -d`, and open the same URL. A rebuild is needed after
Dockerfile/startup-script changes, not after ordinary Python source edits.

The browser port is bound to this computer's loopback interface. See
[display details](gui.md) for the software-rendering baseline.
