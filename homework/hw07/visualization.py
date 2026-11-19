"""Provided visual comparison for HW07; plotting is not assigned."""

import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import numpy as np

from homework.hw07.scenes import arm_problem, base_problem
from intro_robotics.waypoint_metrics import path_length, smoothness_cost
from intro_robotics.waypoint_optimization import (
    optimize_waypoints,
    refine_feasible_path,
    sampled_path_is_free,
)


class OptimizationView:
    def __init__(self):
        base = base_problem()
        base_path, base_costs = optimize_waypoints(
            base["rrt_seed"], base["bounds"], base["circles"]
        )
        direct, direct_costs = optimize_waypoints(
            base["direct_seed"], base["bounds"], base["circles"]
        )
        arm = arm_problem()
        arm_path, _, valid = refine_feasible_path(
            arm["rrt_seed"],
            arm["bounds"],
            arm["clearance"].is_free,
            resolution=0.04,
            iterations=25,
        )
        if not valid:
            raise RuntimeError(
                "The supplied arm seed is invalid at the chosen resolution"
            )
        arm_fine = sampled_path_is_free(arm_path, arm["nominal"].is_free, 0.005)
        print(
            f"Arm path: length={path_length(arm_path):.3f}, smoothness={smoothness_cost(arm_path):.3f}, finer sampled valid={arm_fine}"
        )

        self.fig, (base_ax, arm_ax, cost_ax) = plt.subplots(1, 3, figsize=(15, 4.5))
        base_ax.add_patch(Circle((0, 0), 0.30, color="lightgray"))
        base_ax.add_patch(
            Circle((0, 0), 0.36, fill=False, linestyle="--", color="gray")
        )
        base_ax.plot(
            base_path[:, 0],
            base_path[:, 1],
            "-o",
            color="steelblue",
            markersize=3,
            label="RRT seed",
        )
        base_ax.plot(
            direct[:, 0],
            direct[:, 1],
            "-o",
            color="firebrick",
            markersize=3,
            label="Direct seed",
        )
        base_ax.set(
            xlim=(-1, 1),
            ylim=(-0.8, 0.8),
            xlabel="x (m)",
            ylabel="y (m)",
            title="Two base optimizations",
            aspect="equal",
        )
        base_ax.legend(fontsize="small")
        grid = np.linspace(-2.8, 2.8, 35)
        blocked = np.array(
            [[not arm["clearance"].is_free([x, y]) for x in grid] for y in grid]
        )
        arm_ax.imshow(
            blocked,
            origin="lower",
            extent=(-2.8, 2.8, -2.8, 2.8),
            cmap="Greys",
            alpha=0.25,
        )
        arm_ax.plot(
            arm["rrt_seed"][:, 0],
            arm["rrt_seed"][:, 1],
            "--",
            color="gray",
            label="RRT seed",
        )
        arm_ax.plot(
            arm_path[:, 0],
            arm_path[:, 1],
            "-o",
            color="steelblue",
            markersize=3,
            label="Refined",
        )
        arm_ax.set(
            xlim=(-2.8, 2.8),
            ylim=(-2.8, 2.8),
            xlabel="q1 (rad)",
            ylabel="q2 (rad)",
            title="Arm configuration space",
            aspect="equal",
        )
        arm_ax.legend(fontsize="small")
        cost_ax.semilogy(base_costs, label="Base: RRT seed")
        cost_ax.semilogy(direct_costs, label="Base: direct seed")
        cost_ax.set(
            xlabel="optimizer step",
            ylabel="base objective",
            title="Compare seeds for one task",
        )
        cost_ax.legend(fontsize="small")
        self.fig.tight_layout()

    def show(self):
        plt.show()
