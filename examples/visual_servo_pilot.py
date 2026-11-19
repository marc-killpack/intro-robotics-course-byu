"""Faculty fixed-camera visual-feedback pilot for a stationary target.

The controller sees an RGB image, joint state, and supplied plane calibration.
Object ground truth is used only by the renderer and later for evaluation.
This is an idealized NumPy prototype, not a released homework or final project.
Run from the repository root: python -m examples.visual_servo_pilot
"""

import argparse
from pathlib import Path

import matplotlib
import numpy as np

from examples.oblique_camera_pilot import cameras, scene
from examples.vision_measurement_pilot import fit_homography, red_centroid_in_plane
from intro_robotics import Joint, SerialArm
from intro_robotics.conveyor import ConveyorDemo
from intro_robotics.planar_scene import render_planar_polygons
from intro_robotics.transforms import se3


def visual_command(
    arm, q, image, plane_to_image, gain=1.5, damping=0.08, speed_limit=1.0
):
    """Return bounded joint velocity and measured XY error; stop if target is lost."""
    target = red_centroid_in_plane(image, plane_to_image)
    if target is None:
        return np.zeros(arm.n), None
    tool = arm.fk(q, base=True, tip=True)[:2, 3]
    error = target - tool
    jacobian = arm.jacob_planar(q, base=True, tip=True)[:2]
    # Damped least squares keeps the example's command finite at difficult poses.
    command = jacobian.T @ np.linalg.solve(
        jacobian @ jacobian.T + damping**2 * np.eye(2), gain * error
    )
    return np.clip(command, -speed_limit, speed_limit), error


def run(output, show=False):
    if not show:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    arm = SerialArm(
        [
            Joint("z", tip=se3(translation=[length, 0, 0]), limits=(-2.8, 2.8))
            for length in (0.35, 0.25, 0.15)
        ],
        tip=se3(translation=[0, 0, 0.15]),
    )
    demo = ConveyorDemo(arm, [0.7, -1.1, 0.6], dt=0.04)
    demo.belt_speed = 0.0
    demo.object_position = np.array([0.40, 0.03, 0.0])
    fixed, _, _ = cameras()
    _, _, marks, _ = scene(demo.object_position[0])
    pixels, _, visible = fixed.project(np.column_stack((marks, np.zeros(len(marks)))))
    if not np.all(visible):
        raise RuntimeError("The provided calibration points must be visible")
    plane_to_image = fit_homography(marks, pixels)

    times, tools, errors = [], [], []
    dropout_steps = range(20, 25)
    reached = False
    for i in range(250):
        # The renderer is part of the simulated environment, not the controller.
        polygons, colors, _, _ = scene(demo.object_position[0])
        image = render_planar_polygons(fixed, polygons, colors)
        if i in dropout_steps:
            image[:] = 235  # A short simulated camera/detection failure.
        command, error = visual_command(
            arm, demo.q, image, plane_to_image, speed_limit=demo.speed_limit
        )
        if error is not None and np.linalg.norm(error) < 0.008:
            command = np.zeros(arm.n)
        demo.step(command)
        times.append(demo.time)
        tools.append(demo.tool_pose()[:2, 3].copy())
        errors.append(np.nan if error is None else np.linalg.norm(error))
        if (
            error is not None
            and np.linalg.norm(error) < 0.008
            and np.linalg.norm(demo.velocity) < 0.05
        ):
            reached = True
            break

    tools = np.asarray(tools)
    # Ground truth is used for this faculty evaluation only.
    true_error = np.linalg.norm(tools[-1] - demo.object_position[:2])
    fig, (path_ax, error_ax) = plt.subplots(1, 2, figsize=(10, 4))
    path_ax.plot(tools[:, 0], tools[:, 1], color="steelblue", label="Tool path")
    path_ax.plot(*tools[0], "go", label="Start")
    path_ax.plot(
        *demo.object_position[:2], "r*", markersize=12, label="Target (faculty truth)"
    )
    path_ax.set(
        xlim=(0.3, 0.75),
        ylim=(-0.05, 0.30),
        xlabel="world x (m)",
        ylabel="world y (m)",
        title="Stationary target",
        aspect="equal",
    )
    path_ax.legend(fontsize="small")
    error_ax.plot(times, errors, label="Image-estimated XY error")
    error_ax.axvspan(
        20 * demo.dt, 25 * demo.dt, color="gray", alpha=0.2, label="Detection loss"
    )
    error_ax.set(
        xlabel="simulated time (s)", ylabel="error (m)", title="Bounded visual feedback"
    )
    error_ax.legend(fontsize="small")
    fig.tight_layout()
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=150)
    if show:
        plt.show()
    plt.close(fig)
    print(
        f"reached={reached}; simulated_seconds={demo.time:.2f}; final_ground_truth_error={true_error:.4f} m"
    )
    print(f"Saved {output}; detection-loss frames requested zero velocity.")
    if not reached:
        raise RuntimeError(
            "The stationary-target example did not converge within its budget"
        )
    return true_error


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="tmp/vision-pilot/visual-servo.png")
    parser.add_argument("--show", action="store_true")
    args = parser.parse_args()
    run(args.output, args.show)
