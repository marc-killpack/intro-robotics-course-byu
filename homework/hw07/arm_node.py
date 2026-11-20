"""HW07 problem 5: an arm node that follows a received JointTrajectory.

Complete receive_trajectory() and publish_joint_state(). The node subscribes
to /hw07/trajectory and, 50 times per second, publishes where the joints
should be now on /hw07/joint_states, which robot_state_publisher turns into
TF for RViz. Run it in the course container from /workspace:

    python3 -m homework.hw07.arm_node

Until a trajectory arrives the node publishes nothing, so RViz shows the
arm only once it has a motion to follow. A new trajectory restarts the clock.
"""

import numpy as np
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory

from homework.hw07.path_publisher import latched_qos
from homework.hw07.trajectory import interpolate


class ArmNode(Node):
    def __init__(self):
        super().__init__("hw07_arm")
        self.publisher = self.create_publisher(JointState, "/hw07/joint_states", 10)
        self.subscription = self.create_subscription(
            JointTrajectory, "/hw07/trajectory", self.receive_trajectory, latched_qos()
        )
        self.names = None  # joint names from the trajectory
        self.times = None  # waypoint times in seconds, shape (N,)
        self.path = None  # waypoint positions, shape (N, joints)
        self.start_time = None  # rclpy Time when the trajectory arrived
        self.timer = self.create_timer(0.02, self.publish_joint_state)

    def receive_trajectory(self, message):
        """Store the names, waypoint times (seconds), positions, and start time."""
        # HW07: convert each point's time_from_start (sec + nanosec) to seconds.
        # BEGIN SOLUTION
        self.names = list(message.joint_names)
        self.times = np.array(
            [p.time_from_start.sec + p.time_from_start.nanosec * 1e-9 for p in message.points]
        )
        self.path = np.array([list(p.positions) for p in message.points])
        self.start_time = self.get_clock().now()
        self.get_logger().info(
            f"Received {len(self.times)} waypoints lasting {self.times[-1]:.2f} s"
        )
        return
        # END SOLUTION
        raise NotImplementedError("HW07: implement receive_trajectory(message)")

    def publish_joint_state(self):
        """A timer calls this every 0.02 s. Publish nothing before a trajectory."""
        if self.start_time is None:
            return
        now = self.get_clock().now()
        elapsed = (now - self.start_time).nanoseconds / 1e9
        # HW07: interpolate at the elapsed time and publish a JointState with
        # stamp, names, positions, and velocities (lists of floats).
        # BEGIN SOLUTION
        q, dq = interpolate(self.times, self.path, elapsed)
        message = JointState()
        message.header.stamp = now.to_msg()
        message.name = self.names
        message.position = [float(v) for v in q]
        message.velocity = [float(v) for v in dq]
        self.publisher.publish(message)
        return
        # END SOLUTION
        raise NotImplementedError("HW07: implement publish_joint_state()")


def main():
    rclpy.init()
    node = ArmNode()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass  # Ctrl+C
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
