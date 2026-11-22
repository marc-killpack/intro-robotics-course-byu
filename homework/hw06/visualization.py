"""Provided 2D views for HW06; drawing code is not assigned."""

import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import numpy as np

from homework.hw06.scenes import arm_scene, base_scene
from intro_robotics.planning import arm_segments
from intro_robotics.rrt import rrt_connect


class PlanningView:
    def __init__(self):
        start, goal, bounds, is_free = base_scene()
        base_path = rrt_connect(
            start,
            goal,
            bounds,
            is_free,
            step=0.2,
            resolution=0.02,
            iterations=500,
            seed=12,
        )
        arm, scene, start, goal, bounds = arm_scene()
        arm_path = rrt_connect(
            start,
            goal,
            bounds,
            scene.is_free,
            step=0.3,
            resolution=0.04,
            iterations=500,
            seed=3,
        )
        if base_path is None or arm_path is None:
            raise RuntimeError(
                "A planning attempt failed. Inspect your code or try a different seed."
            )

        self.fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
        base_ax = axes[0]
        config_ax = axes[1]
        arm_ax = axes[2]
        base_ax.add_patch(Circle((0, 0), 0.30, color="lightgray"))
        base_ax.add_patch(
            Circle((0, 0), 0.36, fill=False, linestyle="--", color="gray")
        )
        base_ax.plot(
            base_path[:, 0], base_path[:, 1], "-o", color="steelblue", markersize=3
        )
        base_ax.plot(base_path[0, 0], base_path[0, 1], "go", label="Start")
        base_ax.plot(base_path[-1, 0], base_path[-1, 1], "r*", markersize=10, label="Goal")
        base_ax.set(
            xlim=(-1, 1),
            ylim=(-1, 1),
            xlabel="x (m)",
            ylabel="y (m)",
            title="Circular base",
            aspect="equal",
        )
        base_ax.legend(loc="upper right", fontsize="small")

        # Shade blocked configurations: row j is q2 = grid[j], column i is q1 = grid[i].
        grid = np.linspace(-2.8, 2.8, 45)
        blocked = np.zeros((len(grid), len(grid)), dtype=bool)
        for j in range(len(grid)):
            for i in range(len(grid)):
                blocked[j, i] = not scene.is_free([grid[i], grid[j]])
        config_ax.imshow(
            blocked,
            origin="lower",
            extent=(-2.8, 2.8, -2.8, 2.8),
            cmap="Greys",
            alpha=0.32,
        )
        config_ax.plot(
            arm_path[:, 0], arm_path[:, 1], "-o", color="steelblue", markersize=3
        )
        config_ax.plot(arm_path[0, 0], arm_path[0, 1], "go")
        config_ax.plot(arm_path[-1, 0], arm_path[-1, 1], "r*", markersize=10)
        config_ax.set(
            xlabel="q1 (rad)",
            ylabel="q2 (rad)",
            title="Arm configuration space",
            aspect="equal",
        )

        arm_ax.add_patch(Circle((0.55, 0), 0.07, color="gray"))
        for index in np.unique(np.linspace(0, len(arm_path) - 1, 7, dtype=int)):
            if index == 0:
                color = "green"
            elif index == len(arm_path) - 1:
                color = "firebrick"
            else:
                color = "steelblue"
            for segment in arm_segments(arm, arm_path[index]):
                start = segment[1]
                end = segment[2]
                arm_ax.plot(
                    [start[0], end[0]],
                    [start[1], end[1]],
                    "o-",
                    color=color,
                    alpha=0.75,
                    linewidth=2,
                )
        arm_ax.set(
            xlim=(-0.75, 0.75),
            ylim=(-0.75, 0.75),
            xlabel="x (m)",
            ylabel="y (m)",
            title="Arm poses along path",
            aspect="equal",
        )
        self.fig.tight_layout()

    def show(self):
        plt.show()
