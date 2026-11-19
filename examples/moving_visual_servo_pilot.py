"""Faculty pilot: sort one moving object using a fixed-camera image.

The controller uses images, their times, joint state, actuator phase, and the
known bin position. The simulator uses object truth to render the image and
to evaluate the outcome. This idealized NumPy example is not a student lab.
Run: python -m examples.moving_visual_servo_pilot --show
"""

import argparse
from pathlib import Path

import matplotlib
import numpy as np

from examples.conveyor_pilot import make_demo
from examples.oblique_camera_pilot import cameras, scene
from examples.vision_measurement_pilot import fit_homography, red_centroid_in_plane
from intro_robotics.planar_scene import render_planar_polygons


def bounded_command(arm, q, error, feedforward, speed_limit=1.0):
    """Map an XY error and target velocity to bounded joint velocities."""
    jacobian = arm.jacob_planar(q, base=True, tip=True)[:2]
    desired = 2.0 * error + feedforward
    command = jacobian.T @ np.linalg.solve(
        jacobian @ jacobian.T + 0.08**2 * np.eye(2), desired
    )
    return np.clip(command, -speed_limit, speed_limit)


def track_image(arm, q, image, plane_to_image, time, previous, velocity, may_pick):
    """Track one image; discard stale measurements and stop when detection is lost."""
    target = red_centroid_in_plane(image, plane_to_image)
    if target is None:
        return np.zeros(arm.n), None, None, np.zeros(2), None
    if previous is None:
        velocity = np.zeros(2)
    else:
        previous_time, previous_target = previous
        measured_velocity = (target - previous_target) / (time - previous_time)
        velocity = 0.8 * velocity + 0.2 * measured_velocity
    tool = arm.fk(q, base=True, tip=True)[:2, 3]
    error = target - tool
    command = bounded_command(arm, q, error, velocity)
    action = (
        "pick"
        if may_pick and previous is not None and np.linalg.norm(error) < 0.012
        else None
    )
    return command, action, (time, target), velocity, np.linalg.norm(error)


def belt_image(camera, object_x, object_on_belt):
    """The simulated camera renders ground truth; the controller sees only pixels."""
    polygons, colors, _, _ = scene(object_x)
    if not object_on_belt:
        # The flat renderer does not model an object lifted off the belt.
        keep = [i for i, color in enumerate(colors) if color != [210, 45, 35]]
        polygons = [polygons[i] for i in keep]
        colors = [colors[i] for i in keep]
    return render_planar_polygons(camera, polygons, colors)


def simulate():
    """Run one reproducible scenario and retain faculty evaluation traces."""
    demo, _, _ = make_demo()
    demo.dt = 0.04
    demo.object_position = np.array([0.40, 0.03, 0.0])
    camera, _, _ = cameras()
    _, _, marks, _ = scene(demo.object_position[0])
    pixels, _, _ = camera.project(np.column_stack((marks, np.zeros(len(marks)))))
    plane_to_image = fit_homography(marks, pixels)
    known_bin = demo.bin_position[:2].copy()
    previous = None
    velocity = np.zeros(2)
    times, tools, objects, poses, phases, states = [], [], [], [], [], []
    error_times, errors, lost_commands = [], [], []
    first_image = None
    pick_time = None
    release_time = None
    for i in range(300):
        # Only the simulated renderer and faculty evaluation access object truth.
        image = belt_image(camera, demo.object_position[0], demo.object_state == "belt")
        if first_image is None:
            first_image = image.copy()
        if 20 <= i < 25:
            image[:] = 235
        command = np.zeros(demo.arm.n)
        action = None
        error = None
        if demo.phase in {"idle", "lowering"}:
            command, action, previous, velocity, error = track_image(
                demo.arm,
                demo.q,
                image,
                plane_to_image,
                demo.time,
                previous,
                velocity,
                demo.phase == "idle",
            )
        elif demo.phase == "holding":
            tool = demo.arm.fk(demo.q, base=True, tip=True)[:2, 3]
            bin_error = known_bin - tool
            command = bounded_command(demo.arm, demo.q, bin_error, np.zeros(2))
            if np.linalg.norm(bin_error) < 0.02:
                action = "release"
        else:
            previous = None
            velocity = np.zeros(2)
        if 20 <= i < 25:
            lost_commands.append(command.copy())
        if action == "pick":
            pick_time = demo.time
        if action == "release":
            release_time = demo.time
        error_times.append(demo.time)
        demo.step(command, action)
        times.append(demo.time)
        tools.append(demo.tool_pose()[:3, 3].copy())
        objects.append(demo.object_position.copy())
        poses.append(demo.q.copy())
        phases.append(demo.phase)
        states.append(demo.object_state)
        errors.append(np.nan if error is None else error)
        if demo.object_state in {"sorted", "dropped", "missed"}:
            break
    return {
        "demo": demo,
        "times": np.array(times),
        "tools": np.array(tools),
        "objects": np.array(objects),
        "poses": np.array(poses),
        "phases": phases,
        "states": states,
        "error_times": np.array(error_times),
        "errors": np.array(errors),
        "lost_commands": np.array(lost_commands),
        "first_image": first_image,
        "pick_time": pick_time,
        "release_time": release_time,
        "bin": known_bin,
    }


def save_animation(result, output):
    """Save a top-down faculty visualization; the controller never sees this view."""
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation, PillowWriter
    from matplotlib.patches import Rectangle

    demo = result["demo"]
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.add_patch(Rectangle((0.10, -0.05), 0.62, 0.16, color="lightgray"))
    ax.plot(*result["bin"], "gs", markersize=13, label="Bin")
    (arm_line,) = ax.plot([], [], "o-", color="steelblue", linewidth=4, label="Arm")
    (object_point,) = ax.plot([], [], "ro", markersize=10, label="Object")
    status = ax.text(0.02, 0.98, "", transform=ax.transAxes, va="top")
    ax.set(
        xlim=(-0.1, 0.8),
        ylim=(-0.3, 0.5),
        xlabel="world x (m)",
        ylabel="world y (m)",
        title="Faculty conveyor pilot (top view)",
        aspect="equal",
    )
    ax.legend(loc="lower left", fontsize="small")

    def draw(i):
        q = result["poses"][i]
        points = np.array(
            [demo.arm.fk(q, j, base=True)[:2, 3] for j in range(demo.arm.n + 1)]
        )
        arm_line.set_data(points[:, 0], points[:, 1])
        object_point.set_data([result["objects"][i, 0]], [result["objects"][i, 1]])
        status.set_text(
            f"t = {result['times'][i]:.2f} s   phase = {result['phases'][i]}\n"
            f"tool height = {result['tools'][i, 2]:.2f} m   object = {result['states'][i]}"
        )
        return arm_line, object_point, status

    frame_indices = list(range(0, len(result["times"]), 2))
    if frame_indices[-1] != len(result["times"]) - 1:
        frame_indices.append(len(result["times"]) - 1)
    animation = FuncAnimation(fig, draw, frames=frame_indices, interval=80, blit=True)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    animation.save(output, writer=PillowWriter(fps=12.5))
    plt.close(fig)
    print(f"Saved {output}; top view uses faculty truth for display only.")


def run(output, show=False, animation=None):
    if not show:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    result = simulate()
    demo = result["demo"]
    times, tools, objects = result["times"], result["tools"], result["objects"]
    fig, axes = plt.subplots(2, 2, figsize=(11, 8))
    axes[0, 0].imshow(result["first_image"])
    axes[0, 0].set(
        title="Fixed camera: first frame", xlabel="u (pixels)", ylabel="v (pixels)"
    )
    axes[0, 1].plot(objects[:, 0], objects[:, 1], "r--", label="Object (faculty truth)")
    axes[0, 1].plot(tools[:, 0], tools[:, 1], color="steelblue", label="Tool")
    axes[0, 1].plot(*result["bin"], "gs", label="Known bin")
    axes[0, 1].set(
        title="Moving-object sort",
        xlabel="world x (m)",
        ylabel="world y (m)",
        aspect="equal",
    )
    axes[0, 1].legend(fontsize="small")
    axes[1, 0].plot(
        result["error_times"], result["errors"], label="Image-estimated error"
    )
    axes[1, 0].axvspan(
        20 * demo.dt, 25 * demo.dt, color="gray", alpha=0.2, label="Detection loss"
    )
    axes[1, 0].set(
        title="Tracking error", xlabel="simulated time (s)", ylabel="XY error (m)"
    )
    axes[1, 0].legend(fontsize="small")
    axes[1, 1].plot(times, tools[:, 2], label="Tool height")
    for label, when in (
        ("Pick request", result["pick_time"]),
        ("Release request", result["release_time"]),
    ):
        if when is not None:
            axes[1, 1].axvline(when, linestyle="--", label=label)
    axes[1, 1].set(
        title="Timed vertical stroke", xlabel="simulated time (s)", ylabel="height (m)"
    )
    axes[1, 1].legend(fontsize="small")
    fig.tight_layout()
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=150)
    if show:
        plt.show()
    plt.close(fig)
    print(
        f"state={demo.object_state}; score={demo.score}; simulated_seconds={demo.time:.2f}; failed_picks={demo.failed_picks}; limit_hits={demo.limit_hits}"
    )
    print(f"Saved {output}; detection-loss frames requested zero velocity.")
    if animation is not None:
        save_animation(result, animation)
    if demo.score != 1:
        raise RuntimeError(
            "The fixed-camera moving-object pilot did not sort the object"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="tmp/vision-pilot/moving-sort.png")
    parser.add_argument("--show", action="store_true")
    parser.add_argument("--animation", help="Save an optional top-down GIF")
    args = parser.parse_args()
    run(args.output, args.show, args.animation)
