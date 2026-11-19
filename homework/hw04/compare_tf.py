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

from homework.models import spatial_arm
from intro_robotics import SerialArm
from intro_robotics.transforms import rotz, se3

JOINT_NAMES = ["joint1", "joint2", "joint3"]


def placed_arm():
    """spatial_arm() with problem 4(a)'s world placement and tool offset."""
    return SerialArm(
        spatial_arm().joints,
        base=se3(rotz(np.pi / 2), [1, 0.2, 0]),
        tip=se3(translation=[0, 0, 0.1]),
    )


def main():
    import rclpy
    from rclpy.node import Node
    from rclpy.time import Time
    from sensor_msgs.msg import JointState
    from tf2_ros import Buffer, TransformException, TransformListener

    from homework.ros_frames import quaternion_to_rotation

    arm = placed_arm()
    rclpy.init()
    node = Node("hw04_compare_tf")
    buffer = Buffer()
    TransformListener(buffer, node)
    latest = {}

    def store(message):
        latest.update(zip(message.name, message.position))

    def compare():
        if not all(name in latest for name in JOINT_NAMES):
            print("Waiting for /hw04/joint_states (is view_arm.launch.py running?)")
            return
        try:
            stamped = buffer.lookup_transform("world", "arm_tool", Time())
        except TransformException as error:
            print(f"TF has no world -> arm_tool yet; check your URDF joints. ({error})")
            return
        q = np.array([latest[name] for name in JOINT_NAMES])
        t, r = stamped.transform.translation, stamped.transform.rotation
        tf_position = np.array([t.x, t.y, t.z])
        tf_rotation = quaternion_to_rotation(r.x, r.y, r.z, r.w)
        pose = arm.fk(q, base=True, tip=True)
        np.set_printoptions(precision=4, suppress=True)
        print(f"q = {q}")
        print(f"  TF position: {tf_position}   fk position: {pose[:3, 3]}")
        print(f"  position difference {np.linalg.norm(tf_position - pose[:3, 3]):.2e} m, "
              f"largest rotation-entry difference {np.abs(tf_rotation - pose[:3, :3]).max():.2e}")

    node.create_subscription(JointState, "/hw04/joint_states", store, 10)
    node.create_timer(1.0, compare)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
