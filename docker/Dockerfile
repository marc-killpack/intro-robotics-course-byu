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
        python3-numpy \
        python3-matplotlib \
        python3-tk \
        python3-setuptools \
        python3-wheel \
        python3-colcon-common-extensions \
        python3-rosdep \
        git \
        nano \
        mesa-utils \
        libxcb-cursor0 \
        libxkbcommon-x11-0 \
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
RUN python3 -m venv --system-site-packages /home/student/.venv \
    && /home/student/.venv/bin/python -m pip install --no-cache-dir --no-deps \
        opencv-python==4.10.0.84 \
        PySide6==6.8.3 PySide6-Essentials==6.8.3 PySide6-Addons==6.8.3 \
        shiboken6==6.8.3 pyqtgraph==0.14.0 PyOpenGL==3.1.10 colorama==0.4.6 \
    && /home/student/.venv/bin/python -c "import cv2, numpy, pyqtgraph, OpenGL; from PySide6 import QtCore; print('OpenCV', cv2.__version__, 'NumPy', numpy.__version__, 'Qt', QtCore.__version__)"
ENV PATH="/home/student/.venv/bin:${PATH}"
WORKDIR /workspace
CMD ["/usr/local/bin/start-course-gui"]

