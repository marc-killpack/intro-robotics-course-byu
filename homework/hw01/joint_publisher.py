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
        head_angle = 1.5 * math.sin(elapsed*2*math.pi*0.25)  # head moves back and forth
        left_leg_angle = 0.5 * math.sin(elapsed * 2 * math.pi)  # left leg moves up and down
        right_leg_angle = -0.5 * math.sin(elapsed * 2 * math.pi)  # right leg moves opposite to left leg

        return [head_angle, left_leg_angle, right_leg_angle]
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
    # The steps below are the standard pattern for starting and stopping
    # almost every Python ROS 2 node. Expect to see this same shape in
    # future assignments; usually only the node class name changes.

    # 1. Start ROS. This connects this program to the ROS system so it can
    #    talk to other nodes. It must run before any node is created.
    rclpy.init()

    # 2. Create our node. Running __init__ above sets up the publisher and
    #    the timer, but nothing is published yet.
    node = JointPublisher()

    try:
        # 3. Hand control to ROS. spin() waits for events (here, the timer
        #    firing every 0.1 s based on the defintion in the __init__ method) 
        # and calls the matching method each time.
        #    It keeps running until the program is stopped, which is why
        #    our own code never needs a while loop.
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        # 4. Pressing Ctrl+C (KeyboardInterrupt), or ROS being shut down
        #    from outside (ExternalShutdownException), stops spin().
        #    These are normal ways to quit, so we ignore them instead of
        #    printing an error.
        pass
    finally:
        # 5. Clean up. The finally block always runs, even after an error,
        #    so the node is removed and ROS is shut down properly.
        node.destroy_node()
        # rclpy.ok() is True while ROS is still running. Checking it first
        # avoids shutting ROS down twice if it was already stopped.
        if rclpy.ok():
            rclpy.shutdown()


# Standard Python (not ROS-specific): this is True only when the file is run
# directly, e.g. "python3 joint_publisher.py". If another file imports this
# one (for example, a grading test), main() does not start automatically.
if __name__ == "__main__":
    main()
