"""HW03 problem 4: broadcast the world/base/camera/object frames as static TF.

Complete frame_transforms(). The supplied main() publishes your transforms
with a static TF broadcaster and keeps them available until Ctrl+C. Run it in
the course container from /workspace:

    python3 -m homework.hw03.frame_broadcaster

Then check the chain in a second container shell, for example:

    ros2 run tf2_ros tf2_echo base object
"""

import numpy as np

from intro_robotics.transforms import inv, rotz, se3

# The measured object point from problem 2, in camera coordinates (meters).
P_C = np.array([0.1, 0.05, 0.8])


def frame_transforms():
    """Return a list of (parent, child, T_parent_child) for the four frames.

    Use the frame names "world", "base", "camera", and "object". Each matrix
    is the pose of the child expressed in its parent. Publish base and camera
    as children of world, and object as a child of camera, with the object
    frame at P_C and oriented like the world frame. Use your se3 and inv.
    """
    # HW03: build T_W_B and T_W_C from problem 2 with se3, then T_C_O.
    # BEGIN SOLUTION
    t_w_b = se3(rotz(np.pi / 2), [0.1, 0.1, 0])
    t_w_c = se3(np.diag([1.0, -1.0, -1.0]), [0.4, -0.2, 0.8])
    t_c_o = se3(inv(t_w_c)[:3, :3], P_C)
    return [
        ("world", "base", t_w_b),
        ("world", "camera", t_w_c),
        ("camera", "object", t_c_o),
    ]
    # END SOLUTION
    raise NotImplementedError("HW03: implement frame_transforms()")


def main():
    import rclpy
    from rclpy.node import Node
    from tf2_ros.static_transform_broadcaster import StaticTransformBroadcaster

    from homework.ros_frames import transform_message

    rclpy.init()
    node = Node("hw03_frame_broadcaster")
    broadcaster = StaticTransformBroadcaster(node)
    stamp = node.get_clock().now().to_msg()
    entries = frame_transforms()
    broadcaster.sendTransform(
        [transform_message(parent, child, t, stamp) for parent, child, t in entries]
    )
    for parent, child, t in entries:
        print(f"{parent} -> {child}:\n{np.array2string(np.asarray(t), precision=3, suppress_small=True)}")
    print("Static frames published; press Ctrl+C to stop.")
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
