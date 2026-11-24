"""HW07 problem 5: publish the optimized arm path as a JointTrajectory.

Provided: read trajectory_message() to see how a JointTrajectory is built;
your arm node unpacks the same fields. main() refines the HW06 RRT
path with the supplied optimizer (which calls your smoothness_cost), gives
each waypoint a time with waypoint_times, and starts a small node that
publishes the message once. Run it in the course container from /workspace:

    python3 -m homework.hw07.path_publisher
    python3 -m homework.hw07.path_publisher --seed direct

The trajectory and the markers use "transient local" durability: ROS keeps
the last message and delivers it to a subscriber that starts later.
"""

import argparse
import math

from builtin_interfaces.msg import Duration
from geometry_msgs.msg import Point
import numpy as np
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from visualization_msgs.msg import Marker, MarkerArray

from homework.hw07.scenes import ARM_PLANE_Z, JOINT_NAMES, TOOL_Z, optimized_path
from homework.hw07.trajectory import waypoint_times

OBSTACLE = (0.55, 0.0, 0.07)  # x, y, radius in meters (the HW06 obstacle)


def duration_message(seconds):
    """Provided: a builtin_interfaces/Duration for a time in seconds."""
    whole = math.floor(seconds)
    nanoseconds = int(round((seconds - whole) * 1e9))
    if nanoseconds >= 1_000_000_000:  # rounding reached the next whole second
        whole = whole + 1
        nanoseconds = nanoseconds - 1_000_000_000
    return Duration(sec=int(whole), nanosec=nanoseconds)


def trajectory_message(joint_names, path, times):
    """Provided: a trajectory_msgs/JointTrajectory with one point per waypoint.

    joint_names: list of joint-name strings, one per path column.
    path: N-by-joints waypoint array, rad.
    times: N waypoint times, seconds from the start.

    Fill joint_names and, for each waypoint, a JointTrajectoryPoint whose
    positions are that waypoint (a list of floats) and whose time_from_start
    is its time (use duration_message). Leave header.stamp at zero, which
    means "start when you receive it".
    """
    path = np.asarray(path, dtype=float)
    if path.ndim != 2 or path.shape[1] != len(joint_names) or len(times) != len(path):
        raise ValueError("Use one time per waypoint and one name per joint")
    message = JointTrajectory()
    message.joint_names = list(joint_names)
    for i in range(len(path)):
        point = JointTrajectoryPoint()
        point.positions = [float(value) for value in path[i]]
        point.time_from_start = duration_message(float(times[i]))
        message.points.append(point)
    return message


def marker_messages(arm, path):
    """Provided: the obstacle cylinder and the tool path through the waypoints."""
    obstacle = Marker(ns="hw07", id=0, type=Marker.CYLINDER, action=Marker.ADD)
    obstacle.header.frame_id = "world"
    obstacle.pose.position.x = OBSTACLE[0]
    obstacle.pose.position.y = OBSTACLE[1]
    obstacle.pose.position.z = ARM_PLANE_Z
    obstacle.pose.orientation.w = 1.0
    obstacle.scale.x = 2 * OBSTACLE[2]  # diameter
    obstacle.scale.y = 2 * OBSTACLE[2]
    obstacle.scale.z = 0.4  # height
    obstacle.color.r = 0.8
    obstacle.color.g = 0.2
    obstacle.color.b = 0.2
    obstacle.color.a = 0.6

    tool = Marker(ns="hw07", id=1, type=Marker.LINE_STRIP, action=Marker.ADD)
    tool.header.frame_id = "world"
    tool.pose.orientation.w = 1.0
    tool.scale.x = 0.006  # line width
    tool.color.r = 0.9
    tool.color.g = 0.5
    tool.color.b = 0.1
    tool.color.a = 1.0
    for q in path:
        tool_position = arm.fk(q)[:3, 3]  # the arm's frame 0 is the world origin
        point = Point(x=float(tool_position[0]), y=float(tool_position[1]), z=TOOL_Z)
        tool.points.append(point)
    return MarkerArray(markers=[obstacle, tool])


def latched_qos():
    """Provided: keep the last message for subscribers that start later."""
    return QoSProfile(
        depth=1,
        durability=DurabilityPolicy.TRANSIENT_LOCAL,
        reliability=ReliabilityPolicy.RELIABLE,
    )


class PathPublisher(Node):
    """Publishes the trajectory and the RViz markers once, then stays alive."""

    def __init__(self, arm, path, times):
        super().__init__("hw07_path_publisher")
        self.trajectory_publisher = self.create_publisher(
            JointTrajectory, "/hw07/trajectory", latched_qos()
        )
        self.marker_publisher = self.create_publisher(MarkerArray, "/hw07/markers", latched_qos())
        self.trajectory_publisher.publish(trajectory_message(JOINT_NAMES, path, times))
        self.marker_publisher.publish(marker_messages(arm, path))


def main():
    parser = argparse.ArgumentParser(description="Publish the HW07 arm path once")
    parser.add_argument("--seed", choices=("rrt", "direct"), default="rrt")
    parser.add_argument("--max-speed", type=float, default=0.5, help="rad/s per joint")
    args = parser.parse_args()

    arm, path, valid = optimized_path(args.seed)
    times = waypoint_times(path, args.max_speed)
    print(f"{len(path)} waypoints, {times[-1]:.2f} s, passed the sampled checks: {valid}")
    if not valid:
        print("Warning: this path failed a collision check; it is sent anyway so you can see it.")

    rclpy.init()
    node = PathPublisher(arm, path, times)
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
