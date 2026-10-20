# macOS setup

## Apple Silicon (M-series Macs)

These instructions target any Apple Silicon Mac running a supported version of
macOS and Docker Desktop. The host CPU should report `arm64`. The course image
uses the official multi-architecture ROS 2 Jazzy base, so Docker should choose
a native `linux/arm64` image. RViz appears in a browser; XQuartz is not needed
for this course startup path.

The [ROS Jazzy Docker image announcement](https://discourse.ros.org/t/ros-jazzy-docker-images/37879)
lists ARM64 support for the official base image used here.

1. Install **Docker Desktop for Apple Silicon** and start it. Wait until its
   engine reports that it is running.
2. Open Terminal and confirm the host and Docker architectures:

   ```bash
   uname -m
   docker info --format '{{.OSType}}/{{.Architecture}}'
   docker compose version
   ```

   Expected: `arm64`, then `linux/aarch64` (or `linux/arm64`), and a Compose
   version. Docker Desktop may ask for permission to initialize on first run.
3. From the parent directory that contains this repository, enter it, then
   build and start the environment:

   ```bash
   cd intro-robotics-course
   docker compose build
   docker compose up -d
   ```

4. Open <http://localhost:6080/vnc.html?autoconnect=1&resize=scale> in a
   browser. RViz should show an R2D2-like robot beside a joint-slider window.
   Move `head_yaw` and a leg slider to confirm the picture updates. The first
   launch builds the demo package and may take a moment while Mesa starts.
5. Open a shell for student work:

   ```bash
   docker compose exec course bash
   ```

   `ros2` commands should be available. The repository is mounted at
   `/workspace`; standalone Python work lives under `student_ws/python`, and
   ROS packages go under `student_ws/ros2_ws/src`.
6. When finished, run `docker compose down` from the repository root.

If the page is blank, run `docker compose logs course` and check whether RViz
reported an OpenGL error. If port 6080 is already in use, edit the left side of
the `ports` mapping in `compose.yaml` and use that port in the browser URL.
If the resulting image reports `linux/amd64` on Apple Silicon, inspect the
image choice; emulation is slower than the intended native ARM64 path.

The browser desktop is only published on `127.0.0.1` of the host. Do not
forward it to a public network without adding authentication.

## Intel Mac (validation to do)

The same Compose path should select the `linux/amd64` ROS image on an Intel
Mac, but this configuration has not yet been exercised on one. Before calling
it supported, complete these checks on an Intel Mac:

1. Record the macOS and Docker Desktop versions, and confirm `uname -m`
   reports `x86_64`.
2. Run `docker info --format '{{.OSType}}/{{.Architecture}}'` and note the
   Docker engine architecture.
3. From the repository root, run `docker compose build` and
   `docker compose up -d`. Record any package or image resolution errors.
4. Open <http://localhost:6080/vnc.html?autoconnect=1&resize=scale> and
   confirm RViz appears and the robot moves when a joint slider changes.
5. Run `docker compose exec course bash`, try `ros2 topic list`, and record
   `docker compose logs course` if the GUI does not render.
6. Add the tested macOS/Docker versions, actual results, and any Intel-only
   fixes here before distributing these instructions to Intel Mac students.

