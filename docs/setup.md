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

## Host terminal versus container shell

Use a host terminal for `docker compose ...` commands. To get a ROS-enabled
**Linux shell inside the container**, run:

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

## Python mathematics homeworks

HW02--HW05 use this same container and browser desktop. The image includes
NumPy, Matplotlib, and Tk. The revised Dockerfile also installs OpenCV 4.10
in that virtual environment for the vision unit; rebuild the image to obtain
it. Startup installs the course package from your mounted source. Your host
editor still edits the files you submit. Follow
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

If you received these Dockerfile/startup updates after building an older
image, run this in a **host terminal**:

```text
docker compose build
docker compose up -d --force-recreate
docker compose exec course bash
```

Then, in the **container shell**:

```text
cd /workspace
python -m homework.hw02.hw02_rotations --show
```

Complete the assigned methods first. `--show` opens Matplotlib on the same
browser desktop; move/minimize RViz if needed. `--save tmp/hw02.png` saves
the scene without opening a figure. Run modules from `/workspace` so the
provided homework support imports correctly.

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
