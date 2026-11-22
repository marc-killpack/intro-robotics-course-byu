"""Provided HW04 problem 5 check: print TF's tool pose beside your fk(q).

Start the arm first (ros2 launch homework/hw04/view_arm.launch.py), then in a
second container shell from /workspace:

    python3 -m homework.hw04.compare_tf

Once a second it reads the slider joint angles, asks TF for the pose of
arm_tool in world (computed by ROS from your URDF), and prints it next to
fk(q, base=True, tip=True) from your SerialArm. Hold the sliders still while
comparing; the two readings are taken a few milliseconds apart.
"""

import numpy as np
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.time import Time
from sensor_msgs.msg import JointState
from tf2_ros import Buffer, TransformException, TransformListener

from homework.models import placed_arm
from homework.ros_frames import quaternion_to_rotation

JOINT_NAMES = ["joint1", "joint2", "joint3"]


class CompareTF(Node):
    """Subscribes to the slider joint states and asks TF for the tool pose once a second."""

    def __init__(self):
        super().__init__("hw04_compare_tf")
        self.arm = placed_arm()
        self.joint_angles = {}  # the latest angle for each joint name
        self.buffer = Buffer()
        self.listener = TransformListener(self.buffer, self)
        self.subscription = self.create_subscription(
            JointState, "/hw04/joint_states", self.store_joint_state, 10
        )
        self.timer = self.create_timer(1.0, self.compare)

    def store_joint_state(self, message):
        for i in range(len(message.name)):
            self.joint_angles[message.name[i]] = message.position[i]

    def compare(self):
        for name in JOINT_NAMES:
            if name not in self.joint_angles:
                print("Waiting for /hw04/joint_states (is view_arm.launch.py running?)")
                return
        try:
            stamped = self.buffer.lookup_transform("world", "arm_tool", Time())
        except TransformException as error:
            print(f"TF has no world -> arm_tool yet; check your URDF joints. ({error})")
            return

        q = []
        for name in JOINT_NAMES:
            q.append(self.joint_angles[name])
        q = np.array(q)
        translation = stamped.transform.translation
        rotation = stamped.transform.rotation
        tf_position = np.array([translation.x, translation.y, translation.z])
        tf_rotation = quaternion_to_rotation(rotation.x, rotation.y, rotation.z, rotation.w)

        pose = self.arm.fk(q, base=True, tip=True)
        position_difference = np.linalg.norm(tf_position - pose[:3, 3])
        rotation_difference = np.max(np.abs(tf_rotation - pose[:3, :3]))
        np.set_printoptions(precision=4, suppress=True)
        print(f"q = {q}")
        print(f"  TF position: {tf_position}   fk position: {pose[:3, 3]}")
        print(f"  position difference {position_difference:.2e} m, "
              f"largest rotation-entry difference {rotation_difference:.2e}")


def main():
    rclpy.init()
    node = CompareTF()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
