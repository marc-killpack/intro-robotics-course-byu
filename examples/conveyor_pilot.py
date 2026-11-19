"""Headless one-object integration pilot; uses true positions for debugging.

This supplied reference is not a student vision controller or grading policy.
Later labs must estimate targets from the selected camera's images instead.
"""

import argparse
from pathlib import Path

import matplotlib
import numpy as np

from intro_robotics import Joint, SerialArm
from intro_robotics.camera import Camera
from intro_robotics.conveyor import ConveyorDemo
from intro_robotics.transforms import se3


def make_demo():
    arm = SerialArm(
        [
            Joint("z", tip=se3(translation=[length, 0, 0]), limits=[-2.8, 2.8])
            for length in [0.35, 0.25, 0.15]
        ],
        tip=se3(translation=[0, 0, 0.15]),
    )
    demo = ConveyorDemo(arm, [0.7, -1.1, 0.6])
    optical_down = np.diag([1.0, -1.0, -1.0])
    fixed = Camera(se3(optical_down, [0.4, 0.1, 0.9]))
    mounted = Camera(se3(optical_down, [0, 0, 0.6]), mount="tool")
    return demo, fixed, mounted


def run(output):
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    demo, fixed, mounted = make_demo()
    plt.imsave(output / "fixed-camera.png", demo.image(fixed))
    plt.imsave(output / "tool-camera.png", demo.image(mounted))
    times, tools, objects = [], [], []
    for _ in range(1500):
        tool = demo.tool_pose()[:3, 3]
        target = (
            demo.object_position if demo.object_state == "belt" else demo.bin_position
        )
        error = target[:2] - tool[:2]
        task_velocity = np.array([2 * error[0], 2 * error[1], 0.0])
        if demo.object_state == "belt":
            task_velocity[0] += demo.belt_speed
        jacobian = demo.arm.jacob_planar(demo.q, base=True, tip=True)
        # Supplied bounded least-squares control for this pilot, not assigned IK.
        command = np.linalg.lstsq(jacobian, task_velocity, rcond=None)[0]
        action = None
        if demo.phase == "idle" and np.linalg.norm(error) < 0.012:
            action = "pick"
        if demo.phase == "holding" and np.linalg.norm(error) < 0.025:
            action = "release"
        demo.step(command, action)
        times.append(demo.time)
        tools.append(demo.tool_pose()[:3, 3])
        objects.append(demo.object_position.copy())
        if demo.object_state in {"sorted", "dropped", "missed"}:
            break
    tools, objects = np.asarray(tools), np.asarray(objects)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].plot(objects[:, 0], objects[:, 1], label="Object")
    axes[0].plot(tools[:, 0], tools[:, 1], label="Tool")
    axes[0].plot(*demo.bin_position[:2], "gs", label="Bin")
    axes[0].set(
        xlabel="x (m)", ylabel="y (m)", title="One-object sorting pilot", aspect="equal"
    )
    axes[0].legend()
    axes[1].plot(times, tools[:, 2])
    axes[1].set(
        xlabel="Simulated time (s)",
        ylabel="Tool height (m)",
        title="Timed pickup and lift",
    )
    fig.tight_layout()
    fig.savefig(output / "pilot.png", dpi=150)
    plt.close(fig)
    print(
        f"state={demo.object_state}; score={demo.score}; simulated_seconds={demo.time:.2f}; failed_picks={demo.failed_picks}; limit_hits={demo.limit_hits}"
    )
    if demo.score != 1:
        raise RuntimeError("Reference pilot did not sort the object")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="tmp/conveyor-pilot")
    run(parser.parse_args().output)
