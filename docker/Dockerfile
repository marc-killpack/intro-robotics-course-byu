FROM ros:jazzy-ros-base

ENV DEBIAN_FRONTEND=noninteractive \
    LIBGL_ALWAYS_SOFTWARE=1 \
    QT_X11_NO_MITSHM=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        ros-jazzy-rviz2 \
        ros-jazzy-robot-state-publisher \
        ros-jazzy-joint-state-publisher-gui \
        ros-jazzy-ros2launch \
        ros-jazzy-ament-cmake \
        python3-pip \
        python3-venv \
        python3-colcon-common-extensions \
        python3-rosdep \
        git \
        nano \
        mesa-utils \
        xvfb \
        x11vnc \
        novnc \
        websockify \
        openbox \
        x11-utils \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --user-group --shell /bin/bash student \
    && mkdir -p /workspace/student_ws/ros2_ws/src /workspace/student_ws/python \
    && mkdir -p /tmp/.X11-unix \
    && chmod 1777 /tmp/.X11-unix \
    && chown -R student:student /workspace

RUN echo 'source /opt/ros/jazzy/setup.bash' >> /home/student/.bashrc

COPY docker/start-gui.sh /usr/local/bin/start-course-gui
RUN chmod +x /usr/local/bin/start-course-gui

USER student
WORKDIR /workspace
CMD ["/usr/local/bin/start-course-gui"]

