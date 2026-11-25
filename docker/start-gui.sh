#!/usr/bin/env bash
set -eo pipefail

export DISPLAY=:1
export XDG_RUNTIME_DIR=/tmp/runtime-student
mkdir -p "$XDG_RUNTIME_DIR"
chmod 700 "$XDG_RUNTIME_DIR"

# Screen size of the browser desktop. Students can change it with a .env file
# next to compose.yaml (see docs/troubleshooting.md, "Screen size and speed").
screen="${COURSE_SCREEN:-1280x800}"

rm -f /tmp/.X1-lock /tmp/.X11-unix/X1
Xvfb "$DISPLAY" -screen 0 "${screen}x24" +extension GLX -noreset &
xvfb_pid=$!

for attempt in {1..30}; do
    if xdpyinfo -display "$DISPLAY" >/dev/null 2>&1; then
        break
    fi
    if ! kill -0 "$xvfb_pid" 2>/dev/null; then
        echo "Xvfb exited before the display became ready" >&2
        exit 1
    fi
    sleep 0.2
done

if ! xdpyinfo -display "$DISPLAY" >/dev/null 2>&1; then
    echo "Xvfb did not become ready" >&2
    exit 1
fi

openbox &
# Taskbar: shows open windows so a minimized window can be clicked back.
tint2 >/dev/null 2>&1 &
x11vnc -display "$DISPLAY" -forever -shared -nopw -localhost \
    -rfbport 5900 -quiet &
websockify --web=/usr/share/novnc 0.0.0.0:6080 localhost:5900 &
websockify_pid=$!

source /opt/ros/jazzy/setup.bash
if [ -f /workspace/pyproject.toml ]; then
    # Install the mounted student/faculty tree, never a baked-in answer copy.
    python -m pip install --no-deps --no-build-isolation -e /workspace
fi

# Nothing ROS-related starts here: students build the ROS packages with
# colcon and start programs such as the R2D2 demo themselves.
echo "Course desktop ready (screen ${screen})."
echo "Open http://localhost:6080/vnc.html?autoconnect=1&resize=scale in your computer's web browser."
echo "Docker Desktop's dashboard is not the desktop window."

# Keep the container running for as long as the display and web server run.
wait -n "$xvfb_pid" "$websockify_pid"
