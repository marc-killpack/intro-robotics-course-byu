"""HW07 problem 5: publish the optimized arm path as a JointTrajectory.

Complete trajectory_message(). The supplied main() refines the HW06 RRT
path with the supplied optimizer (which calls your smoothness_cost), gives
each waypoint a time with waypoint_times, and publishes your message once.
Run it in the course container from /workspace:

    python3 -m homework.hw07.path_publisher
    python3 -m homework.hw07.path_publisher --seed direct

The trajectory and the markers use "transient local" durability: ROS keeps
the last message and delivers it to a subscriber that starts later.
ROS is imported only inside the functions, so this file imports without ROS.
"""

import argparse
import math

import numpy as np

from homework.hw07.trajectory import waypoint_times

JOINT_NAMES = ["joint1", "joint2"]
ARM_PLANE_Z = 0.2  # height of the moving joints in planar_arm.urdf
TOOL_Z = 0.3  # arm_tool sits 0.1 m above the flange (tool_joint)
OBSTACLE = (0.55, 0.0, 0.07)  # x, y, radius in meters (the HW06 obstacle)


def duration_message(seconds):
    """Provided: a builtin_interfaces/Duration for a time in seconds."""
    from builtin_interfaces.msg import Duration

    whole = math.floor(seconds)
    nanoseconds = int(round((seconds - whole) * 1e9))
    if nanoseconds >= 1_000_000_000:
        whole, nanoseconds = whole + 1, nanoseconds - 1_000_000_000
    return Duration(sec=int(whole), nanosec=nanoseconds)


def trajectory_message(joint_names, path, times):
    """Return a trajectory_msgs/JointTrajectory with one point per waypoint.

    Fill joint_names and, for each waypoint, a JointTrajectoryPoint whose
    positions are that waypoint (a list of floats) and whose time_from_start
    is its time (use duration_message). Leave header.stamp at zero, which
    means "start when you receive it".
    """
    from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

    path = np.asarray(path, dtype=float)
    if path.ndim != 2 or path.shape[1] != len(joint_names) or len(times) != len(path):
        raise ValueError("Use one time per waypoint and one name per joint")
    # HW07: create the message, set joint_names, and append the points.
    # BEGIN SOLUTION
    message = JointTrajectory()
    message.joint_names = list(joint_names)
    for positions, seconds in zip(path, times):
        point = JointTrajectoryPoint()
        point.positions = [float(value) for value in positions]
        point.time_from_start = duration_message(float(seconds))
        message.points.append(point)
    return message
    # END SOLUTION
    raise NotImplementedError("HW07: implement trajectory_message")


def optimized_path(seed="rrt"):
    """Provided: the arm path from problem 4 and whether it passed the checks."""
    from homework.hw07.scenes import arm_problem
    from intro_robotics.waypoint_optimization import refine_feasible_path, sampled_path_is_free

    arm = arm_problem()
    path, _, valid = refine_feasible_path(
        arm[f"{seed}_seed"], arm["bounds"], arm["clearance"].is_free, resolution=0.04
    )
    valid = valid and sampled_path_is_free(path, arm["nominal"].is_free, 0.005)
    return arm["arm"], path, valid


def marker_messages(arm, path):
    """Provided: the obstacle cylinder and the tool path through the waypoints."""
    from geometry_msgs.msg import Point
    from visualization_msgs.msg import Marker, MarkerArray

    x, y, radius = OBSTACLE
    obstacle = Marker(ns="hw07", id=0, type=Marker.CYLINDER, action=Marker.ADD)
    obstacle.header.frame_id = "world"
    obstacle.pose.position.x, obstacle.pose.position.y = x, y
    obstacle.pose.position.z = ARM_PLANE_Z
    obstacle.pose.orientation.w = 1.0
    obstacle.scale.x = obstacle.scale.y = 2 * radius
    obstacle.scale.z = 0.4
    obstacle.color.r, obstacle.color.g, obstacle.color.b, obstacle.color.a = 0.8, 0.2, 0.2, 0.6

    tool = Marker(ns="hw07", id=1, type=Marker.LINE_STRIP, action=Marker.ADD)
    tool.header.frame_id = "world"
    tool.pose.orientation.w = 1.0
    tool.scale.x = 0.006
    tool.color.r, tool.color.g, tool.color.b, tool.color.a = 0.9, 0.5, 0.1, 1.0
    for q in path:
        px, py = arm.fk(q)[:2, 3]
        tool.points.append(Point(x=float(px), y=float(py), z=TOOL_Z))
    return MarkerArray(markers=[obstacle, tool])


def latched_qos():
    """Provided: keep the last message for subscribers that start later."""
    from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy

    return QoSProfile(
        depth=1,
        durability=DurabilityPolicy.TRANSIENT_LOCAL,
        reliability=ReliabilityPolicy.RELIABLE,
    )


def main():
    parser = argparse.ArgumentParser(description="Publish the HW07 arm path once")
    parser.add_argument("--seed", choices=("rrt", "direct"), default="rrt")
    parser.add_argument("--max-speed", type=float, default=0.5, help="rad/s per joint")
    args = parser.parse_args()

    import rclpy
    from rclpy.executors import ExternalShutdownException
    from rclpy.node import Node
    from trajectory_msgs.msg import JointTrajectory
    from visualization_msgs.msg import MarkerArray

    arm, path, valid = optimized_path(args.seed)
    times = waypoint_times(path, args.max_speed)
    print(f"{len(path)} waypoints, {times[-1]:.2f} s, passed the sampled checks: {valid}")
    if not valid:
        print("Warning: this path failed a collision check; it is sent anyway so you can see it.")

    rclpy.init()
    node = Node("hw07_path_publisher")
    trajectory = node.create_publisher(JointTrajectory, "/hw07/trajectory", latched_qos())
    markers = node.create_publisher(MarkerArray, "/hw07/markers", latched_qos())
    trajectory.publish(trajectory_message(JOINT_NAMES, path, times))
    markers.publish(marker_messages(arm, path))
    print("Published /hw07/trajectory and /hw07/markers; press Ctrl+C to stop.")
    try:
        rclpy.spin(node)  # stay alive so late subscribers still receive the message
    except (KeyboardInterrupt, ExternalShutdownException):
        pass  # Ctrl+C
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
