"""Live ROS mode: the supplied simulator node and camera node (one process).

    ros2 launch homework/project/project.launch.py scenario:=s2

Usually started by that launch file, which also starts robot_state_publisher,
the controller node, and RViz. The simulator owns time: on each tick of a
wall-clock timer it advances one control period of simulated time, then
publishes /clock, the joint and actuator state, and both camera images, all
stamped with the same simulated time. Every other node sets use_sim_time.

The camera node renders from the simulator's object truth, so it runs in
this process; it is still a separate node in the ROS graph. Object truth is
never published on a topic the controller reads (the optional truth markers
are for demonstrations only).

Timing matches the graded lockstep runner: the command that answers the
observation at time t is applied over the period after the next one (one
period of delay). If no command arrives for 0.25 s of simulated time, the
simulator applies zero velocity (the watchdog). Live runs depend on how fast
the computer is and are never used for grading.

Topics (relative names; the launch file puts them under /project):

    joint_states                sensor_msgs/JointState   arm joints and pickup_joint
    actuator/state              conveyor_interfaces/PickupState
    fixed_camera/image_raw      sensor_msgs/Image (rgb8) and .../camera_info
    tool_camera/image_raw       sensor_msgs/Image (rgb8) and .../camera_info
    scene_markers               visualization_msgs/MarkerArray (belt, bins, marks)
    truth_markers               visualization_msgs/MarkerArray (only with --truth-markers)
    joint_velocity_command      std_msgs/Float64MultiArray   (subscribed)
    actuator/request            conveyor_interfaces/PickupRequest (subscribed)
    /clock                      rosgraph_msgs/Clock
"""

import argparse
import array
import sys

import numpy as np

from . import ros_bridge
from .contract import REQUESTS
from .scenario import load_scenario
from .simulator import SortingSimulator

WATCHDOG_SECONDS = 0.25


def time_message(seconds):
    from builtin_interfaces.msg import Time

    nanoseconds = int(round(seconds * 1e9))
    return Time(sec=nanoseconds // 1_000_000_000, nanosec=nanoseconds % 1_000_000_000)


def marker_array(descriptions, namespace, stamp, frame="world"):
    from geometry_msgs.msg import Point
    from visualization_msgs.msg import Marker, MarkerArray

    markers = MarkerArray()
    clear = Marker(action=Marker.DELETEALL)
    clear.header.frame_id = frame
    markers.markers.append(clear)
    for i, d in enumerate(descriptions):
        m = Marker(type=d["type"], action=Marker.ADD, ns=namespace, id=i)
        m.header.frame_id, m.header.stamp = frame, stamp
        m.pose.position.x, m.pose.position.y, m.pose.position.z = map(float, d["position"])
        yaw = d.get("yaw", 0.0)
        m.pose.orientation.z, m.pose.orientation.w = float(np.sin(yaw / 2)), float(np.cos(yaw / 2))
        m.scale.x, m.scale.y, m.scale.z = map(float, d["scale"])
        m.color.r, m.color.g, m.color.b, m.color.a = map(float, d["color"])
        m.points = [Point(x=float(x), y=float(y), z=float(z)) for x, y, z in d.get("points", [])]
        markers.markers.append(m)
    return markers


def make_nodes(scenario, seed=None, rate=1.0, truth_markers=False):
    """Build the simulator and camera nodes (rclpy must be initialized)."""
    from rclpy.node import Node
    from rclpy.parameter import Parameter
    from rclpy.qos import DurabilityPolicy, QoSProfile
    from rosgraph_msgs.msg import Clock
    from sensor_msgs.msg import CameraInfo, Image, JointState
    from std_msgs.msg import Float64MultiArray
    from visualization_msgs.msg import MarkerArray

    from conveyor_interfaces.msg import PickupRequest, PickupState

    latched = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL)

    class CameraNode(Node):
        """Renders and publishes both cameras' images at the simulator's request."""

        def __init__(self, simulator):
            super().__init__("conveyor_cameras",
                             parameter_overrides=[Parameter("use_sim_time", value=True)])
            self.sim = simulator
            self.outputs = []
            for name, camera, frame in (("fixed_camera", simulator.fixed_camera, ros_bridge.FIXED_CAMERA_FRAME),
                                        ("tool_camera", simulator.tool_camera, ros_bridge.TOOL_CAMERA_FRAME)):
                info = CameraInfo()
                info.header.frame_id = frame
                info.width, info.height, info.k, info.p = ros_bridge.camera_info_fields(camera)
                info.distortion_model, info.d = "plumb_bob", [0.0] * 5
                info.r = [1.0, 0, 0, 0, 1.0, 0, 0, 0, 1.0]
                self.outputs.append((camera, frame, info,
                                     self.create_publisher(Image, f"{name}/image_raw", 2),
                                     self.create_publisher(CameraInfo, f"{name}/camera_info", 2)))

        def publish(self, stamp):
            for camera, frame, info, image_publisher, info_publisher in self.outputs:
                pixels = self.sim.render(camera)
                message = Image(height=pixels.shape[0], width=pixels.shape[1], encoding="rgb8",
                                is_bigendian=0, step=pixels.shape[1] * 3)
                message.header.stamp, message.header.frame_id = stamp, frame
                message.data = array.array("B", pixels.tobytes())
                image_publisher.publish(message)
                info.header.stamp = stamp
                info_publisher.publish(info)

    class SimulatorNode(Node):
        def __init__(self):
            # The simulator owns time, so it runs on the wall clock (no use_sim_time).
            super().__init__("conveyor_sim")
            self.sim = SortingSimulator(scenario, seed=seed)
            self.cameras = CameraNode(self.sim)
            n, period = self.sim.n, scenario["control_period"]
            self.period = period
            self.zero = (np.zeros(n), "hold")
            self.latest_dq, self.latest_request = np.zeros(n), "hold"
            self.last_command_time = 0.0  # simulated time of the last command received
            self.pending = self.zero
            self.started = self.reported = self.watchdog_on = False
            self.clock = self.create_publisher(Clock, "/clock", 10)
            self.joints = self.create_publisher(JointState, "joint_states", 10)
            self.actuator = self.create_publisher(PickupState, "actuator/state", 10)
            self.create_subscription(Float64MultiArray, "joint_velocity_command", self.on_velocity, 10)
            self.create_subscription(PickupRequest, "actuator/request", self.on_request, 10)
            scene = self.create_publisher(MarkerArray, "scene_markers", latched)
            scene.publish(marker_array(ros_bridge.scene_markers(scenario), "scene", time_message(0.0)))
            self.truth = self.create_publisher(MarkerArray, "truth_markers", 2) if truth_markers else None
            self.timer = self.create_timer(period / rate, self.tick)
            self.get_logger().info(
                f"{scenario['name']}, seed {scenario['seed'] if seed is None else seed}: "
                f"{len(self.sim.objects)} objects, belt {self.sim.belt_speed:.3f} m/s, "
                f"{1 / period:.0f} Hz at {rate:g}x real time")

        def on_velocity(self, message):
            dq = np.asarray(message.data, float)
            if dq.shape != (self.sim.n,) or not np.all(np.isfinite(dq)):
                self.get_logger().warning(f"Ignoring a command with {dq.shape} values; expected {self.sim.n}",
                                          throttle_duration_sec=2.0)
                return
            self.latest_dq = dq
            self.last_command_time = self.sim.time

        def on_request(self, message):
            if message.request not in REQUESTS:
                self.get_logger().warning(f"Ignoring unknown pickup request {message.request!r}")
                return
            if message.request != "hold":
                self.latest_request = message.request

        def tick(self):
            if self.sim.done:
                if not self.reported:
                    self.reported = True
                    c = self.sim.counts
                    self.get_logger().info(
                        f"Episode over at {self.sim.time:.2f} s: score {self.sim.score}, sorted "
                        f"{c['sorted']}/{len(self.sim.objects)}, wrong bin {c['wrong_bin']}, dropped "
                        f"{c['dropped']}, missed {c['missed']}, failed picks {c['failed_picks']}, "
                        f"limit hits {c['limit_hits']}, collisions {c['collisions']}")
                return
            if self.started:
                # One period of delay, as in the lockstep runner: apply what was
                # pending, and make the newest command pending for next period.
                apply = self.pending
                stale = self.sim.time - self.last_command_time > WATCHDOG_SECONDS
                if stale != self.watchdog_on:
                    self.watchdog_on = stale
                    self.get_logger().warning("No command for 0.25 s: commanding zero velocity"
                                              if stale else "Commands resumed")
                self.pending = self.zero if stale else (self.latest_dq, self.latest_request)
                self.latest_request = "hold"  # each request is used once
                self.sim.advance_period(*apply)
            self.started = True
            self.publish_state()

        def publish_state(self):
            stamp = time_message(self.sim.time)
            self.clock.publish(Clock(clock=stamp))
            names, positions, velocities = ros_bridge.joint_state_fields(self.sim)
            joints = JointState(name=names, position=positions, velocity=velocities)
            joints.header.stamp = stamp
            self.joints.publish(joints)
            state = PickupState(phase=self.sim.phase)
            state.header.stamp = stamp
            self.actuator.publish(state)
            self.cameras.publish(stamp)
            if self.truth is not None:
                self.truth.publish(marker_array(ros_bridge.object_markers(self.sim), "objects", stamp))

    simulator = SimulatorNode()
    return simulator, simulator.cameras


def main(argv=None):
    import rclpy
    from rclpy.executors import ExternalShutdownException, SingleThreadedExecutor
    from rclpy.utilities import remove_ros_args

    argv = sys.argv if argv is None else argv
    parser = argparse.ArgumentParser(description="Conveyor simulator and camera nodes")
    parser.add_argument("--scenario", default="s1")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--realism", choices=("on", "off"))
    parser.add_argument("--rate", type=float, default=1.0, help="real-time factor (0.5 = half speed)")
    parser.add_argument("--truth-markers", action="store_true", help="faculty demo: show object truth")
    args = parser.parse_args(remove_ros_args(argv)[1:])
    scenario = load_scenario(args.scenario, realism=None if args.realism is None else args.realism == "on")

    rclpy.init(args=argv)
    nodes = make_nodes(scenario, args.seed, args.rate, args.truth_markers)
    executor = SingleThreadedExecutor()
    for node in nodes:
        executor.add_node(node)
    try:
        executor.spin()
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        for node in nodes:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
