"""Run inside the ROS image to check real timers/messages and stripped stubs.

This is an instructor integration probe, not part of unittest discovery or
the student release. It needs rclpy/sensor_msgs from ROS 2 Jazzy.
"""

import importlib.util
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

import rclpy
from rclpy.executors import SingleThreadedExecutor
from sensor_msgs.msg import JointState

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "homework/hw01"))
from joint_publisher import JointPublisher
from support import JOINT_NAMES, check_joint_positions
from release_tools.student_release import strip_solutions


def main():
    rclpy.init()
    publisher = JointPublisher()
    observer = rclpy.create_node("hw01_instructor_observer")
    messages = []
    subscription = observer.create_subscription(
        JointState, "/joint_states", messages.append, 10
    )
    executor = SingleThreadedExecutor()
    executor.add_node(publisher)
    executor.add_node(observer)
    try:
        deadline = time.monotonic() + 45
        while time.monotonic() < deadline:
            executor.spin_once(timeout_sec=0.1)
            names = set(observer.get_node_names())
            if {"robot_state_publisher", "rviz"}.issubset(names):
                break
        assert {"robot_state_publisher", "rviz"}.issubset(
            names
        ), "Viewer nodes did not start"
        assert "joint_state_publisher" not in names, "Slider publisher must be disabled"
        messages.clear()
        deadline = time.monotonic() + 10
        while len(messages) < 25 and time.monotonic() < deadline:
            executor.spin_once(timeout_sec=0.1)
        assert len(messages) >= 25, "Did not receive timer-driven messages"
        assert (
            observer.count_publishers("/joint_states") == 1
        ), "Competing joint-state publishers"
        print(
            "Publisher mode: RViz and robot-state-publisher present; slider publisher absent."
        )
        stamps = []
        for message in messages:
            assert message.name == JOINT_NAMES
            check_joint_positions(message.position)
            stamps.append(message.header.stamp.sec + message.header.stamp.nanosec / 1e9)
        assert all(after > before for before, after in zip(stamps, stamps[1:]))
        rate = (len(stamps) - 1) / (stamps[-1] - stamps[0])
        assert 5 <= rate <= 20, f"Unexpected timer rate: {rate}"
        heads = [message.position[0] for message in messages]
        assert max(heads) - min(heads) > 0.1, "Head positions did not change"
        print(
            f"Received {len(messages)} bounded, named messages at {rate:.2f} Hz; head motion verified."
        )
    finally:
        executor.shutdown()
        publisher.destroy_node()
        observer.destroy_node()
        rclpy.shutdown()

    source = ROOT / "homework/hw01/joint_publisher.py"
    stripped, count = strip_solutions(source.read_text(), str(source))
    assert count == 2
    with tempfile.TemporaryDirectory(prefix="hw01-student-") as temporary:
        temporary = Path(temporary)
        student_file = temporary / "joint_publisher.py"
        student_file.write_text(stripped)
        shutil.copyfile(source.with_name("support.py"), temporary / "support.py")
        result = subprocess.run(
            [sys.executable, str(student_file)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode != 0
        assert (
            "NotImplementedError: HW01: implement joint_positions(elapsed)"
            in result.stderr
        )

        spec = importlib.util.spec_from_file_location(
            "hw01_student_probe", student_file
        )
        student = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(student)
        student.JointPublisher.joint_positions = lambda self, elapsed: [0, 0, 0]
        rclpy.init()
        node = student.JointPublisher()
        try:
            try:
                node.publish_joint_state()
            except NotImplementedError as error:
                assert "publish_joint_state" in str(error)
            else:
                raise AssertionError(
                    "Second assigned method did not retain its scaffold error"
                )
        finally:
            node.destroy_node()
            rclpy.shutdown()
    print("Both generated student methods retain their expected HW01 errors.")


if __name__ == "__main__":
    main()
