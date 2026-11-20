#!/usr/bin/env bash
set -eo pipefail

export DISPLAY=:1
export XDG_RUNTIME_DIR=/tmp/runtime-student
mkdir -p "$XDG_RUNTIME_DIR"
chmod 700 "$XDG_RUNTIME_DIR"

rm -f /tmp/.X1-lock /tmp/.X11-unix/X1
Xvfb "$DISPLAY" -screen 0 1280x800x24 +extension GLX -noreset &
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
x11vnc -display "$DISPLAY" -forever -shared -nopw -localhost \
    -rfbport 5900 -quiet &
websockify --web=/usr/share/novnc 0.0.0.0:6080 localhost:5900 &

echo "RViz desktop: http://localhost:6080/vnc.html?autoconnect=1&resize=scale"
echo "Open that address in your computer's web browser; Docker Desktop is not the RViz window."
echo "The robot appears after the ROS package finishes building."

source /opt/ros/jazzy/setup.bash
if [ -f /workspace/pyproject.toml ]; then
    # Install the mounted student/faculty tree, never a baked-in answer copy.
    python -m pip install --no-deps --no-build-isolation -e /workspace
fi
cd /workspace/student_ws/ros2_ws
# conveyor_interfaces holds the project's pickup messages; colcon skips it
# with a warning when a student copy does not include it yet.
colcon build --packages-select r2d2_demo conveyor_interfaces
source install/setup.bash
ros2 launch r2d2_demo view_r2d2.launch.py use_joint_gui:="${COURSE_JOINT_GUI:-true}"
