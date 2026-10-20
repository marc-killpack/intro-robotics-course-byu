# GUI setup for RViz

The container starts an R2D2-like robot demo, RViz, and its joint sliders on
a virtual Linux display, then exposes that display through a local browser
page. Students use the same Compose commands on
macOS, Windows, and Linux:

```bash
docker compose build
docker compose up -d
```

Open <http://localhost:6080/vnc.html?autoconnect=1&resize=scale>. Compose
binds port 6080 to the host's loopback address, so this desktop is intended
for use on the same computer. Drag a slider in the **Joint State Publisher**
window and watch the model update in RViz. To stop it, run
`docker compose down`. The [demo README](../student_ws/ros2_ws/src/r2d2_demo/README.md)
explains the ROS 2 topics involved.

This path uses Mesa software rendering, including on Apple Silicon. It avoids
host X11 or GPU driver setup for the first RViz exercise. Graphics-heavy
simulators will need separate evaluation before they are required in class.

For a container shell while RViz is running:

```bash
docker compose exec course bash
```

The shell shares the container's ROS environment and `DISPLAY=:1`, so GUI
programs started there appear on the browser desktop.

For Mac instructions and Intel Mac validation notes, see [macos.md](macos.md).

