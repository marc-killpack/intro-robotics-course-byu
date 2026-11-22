"""HW01: publish joint states using a small node class and a periodic timer.

The provided class owns a publisher, a start time, and a periodic timer.
Implement the two short methods identified by the homework comments.
Run inside the ROS-enabled course shell from /workspace.
"""

import math

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from sensor_msgs.msg import JointState

from support import JOINT_NAMES, check_joint_positions


class JointPublisher(Node):
    def __init__(self):
        super().__init__("hw01_joint_publisher")
        self.publisher = self.create_publisher(JointState, "/joint_states", 10)
        self.start_time = self.get_clock().now()
        self.timer = self.create_timer(0.1, self.publish_joint_state)

    def joint_positions(self, elapsed):
        """Return [head, left leg, right leg] in radians; elapsed is seconds."""
        # HW01: begin with a fixed pose, then make the angles vary smoothly.
        # The provided URDF's bounds are listed in support.py.
        # BEGIN SOLUTION
        phase = 2 * math.pi * elapsed / 5.0
        return [0.7 * math.sin(phase), 0.2 * math.sin(phase), -0.2 * math.sin(phase)]
        # END SOLUTION
        raise NotImplementedError("HW01: implement joint_positions(elapsed)")

    def publish_joint_state(self):
        """A timer calls this method every 0.1 seconds; do not add a while loop."""
        now = self.get_clock().now()
        elapsed = (now - self.start_time).nanoseconds / 1e9
        positions = check_joint_positions(self.joint_positions(elapsed))
        # HW01: create a JointState, fill its stamp, names, and positions,
        # and publish it with self.publisher. Names and positions must align.
        # BEGIN SOLUTION
        message = JointState()
        message.header.stamp = now.to_msg()
        message.name = JOINT_NAMES
        message.position = positions
        self.publisher.publish(message)
        return
        # END SOLUTION
        raise NotImplementedError("HW01: implement publish_joint_state()")


def main():
    rclpy.init()
    node = JointPublisher()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):  # Ctrl+C
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
