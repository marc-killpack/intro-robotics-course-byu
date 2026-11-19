"""Plan a redundant planar arm's path by branching virtual arms (lecture P6).

Faculty example for planning lecture P6 and the reading
docs/readings/position_only_branching.tex, a simplified planar version of
Bodily, Allen, and Killpack, "Motion Planning for Mobile Robots Using Inverse
Kinematics Branching" (ICRA 2017). k copies of one 4-link arm share a fixed
base. Each copy is pulled toward its own point on a vertical line (position
only; the tool's orientation is free) while neighboring copies are kept close
(smooth motion), joints are kept near their centers, and links are pushed off
a circular obstacle. Every iteration is one stacked damped least-squares
solve, the same idea as damped pseudo-inverse IK. Equation numbers in the
comments refer to the reading. NumPy only.

Run: python -m examples.position_only_branching --show
     python -m examples.position_only_branching --save tmp/branching.png
     Options --kappa 0 and --no-obstacle support the reading's questions.
"""

import argparse
from pathlib import Path

import matplotlib
from matplotlib.patches import Circle
import numpy as np

LINKS = np.full(4, 0.2)  # four 0.2 m links, as in the paper's planar example
LIMITS = np.array([[-2.6, 2.6]] * 4)  # joint stops (rad)
CENTER = LIMITS.mean(axis=1)


def joint_points(q):
    """Return the base, the joint locations, and the tool: (n + 1)-by-2."""
    angles = np.cumsum(q)
    steps = LINKS[:, None] * np.column_stack((np.cos(angles), np.sin(angles)))
    return np.vstack((np.zeros(2), np.cumsum(steps, axis=0)))


def point_jacobian(q, point, link):
    """2-by-n Jacobian of a point on `link` (0-based); later joints do not move it.

    For the tool (link n-1, point = tool) this equals the first two rows of
    jacob_planar: column j is z x (point - joint j) = [-(y - yj), x - xj].
    """
    joints = joint_points(q)[:-1]
    jacobian = np.zeros((2, len(q)))
    for j in range(link + 1):
        dx, dy = point - joints[j]
        jacobian[:, j] = [-dy, dx]
    return jacobian


def closest_on_segment(a, b, p):
    t = np.clip(np.dot(p - a, b - a) / np.dot(b - a, b - a), 0.0, 1.0)
    return a + t * (b - a)


def clearance(q, obstacle):
    """Smallest distance from any link segment to the obstacle's edge (m)."""
    points = joint_points(q)
    center, radius = np.asarray(obstacle[:2]), obstacle[2]
    return min(
        np.linalg.norm(closest_on_segment(a, b, center) - center) - radius
        for a, b in zip(points[:-1], points[1:])
    )


def obstacle_rows(q, obstacle, margin, weight):
    """Rows of eq. (5): push each link that is within `margin` of the obstacle."""
    points = joint_points(q)
    center, radius = np.asarray(obstacle[:2]), obstacle[2]
    rows, rhs = [], []
    for link, (a, b) in enumerate(zip(points[:-1], points[1:])):
        near = closest_on_segment(a, b, center)
        offset = near - center
        d = np.linalg.norm(offset) - radius
        if d < margin:
            normal = offset / np.linalg.norm(offset)
            scale = np.sqrt(weight) * (margin - d) / margin
            rows.append(scale * normal @ point_jacobian(q, near, link))
            rhs.append(scale * (margin - d))  # move outward by (margin - d)
    return rows, rhs


def position_errors(q_all, targets):
    return np.array([t - joint_points(q)[-1] for q, t in zip(q_all, targets)])


def branch(
    targets,
    q_start,
    obstacle=None,
    kappa=1.0,
    beta=0.1,
    damping=0.05,
    collision_weight=20.0,
    margin=0.06,
    max_step=0.15,
    iterations=400,
):
    """Return (final configurations, list of configurations per iteration).

    q_start is k-by-n, one row per virtual arm. kappa (smoothness) and beta
    (joint centering) decay as the position error stops improving (section 4).
    """
    k, n = q_start.shape
    q = q_start.copy()
    history = [q.copy()]
    error = np.sum(position_errors(q, targets) ** 2)
    for _ in range(iterations):
        rows, rhs = [], []
        for i in range(k):  # eq. (2): reach each arm's own target
            block = np.zeros((2, k * n))
            block[:, i * n : (i + 1) * n] = point_jacobian(q[i], joint_points(q[i])[-1], n - 1)
            rows.extend(block)
            rhs.extend(targets[i] - joint_points(q[i])[-1])
        for i in range(k - 1):  # eq. (3): neighbors stay close (smooth motion)
            block = np.zeros((n, k * n))
            block[:, i * n : (i + 1) * n] = np.sqrt(kappa) * np.eye(n)
            block[:, (i + 1) * n : (i + 2) * n] = -np.sqrt(kappa) * np.eye(n)
            rows.extend(block)
            rhs.extend(-np.sqrt(kappa) * (q[i] - q[i + 1]))
        rows.extend(np.sqrt(beta) * np.eye(k * n))  # eq. (4): stay near center
        rhs.extend(-np.sqrt(beta) * (q - CENTER).ravel())
        if obstacle is not None:  # eq. (5): links off the obstacle
            for i in range(k):
                more, values = obstacle_rows(q[i], obstacle, margin, collision_weight)
                for row, value in zip(more, values):
                    full = np.zeros(k * n)
                    full[i * n : (i + 1) * n] = row
                    rows.append(full)
                    rhs.append(value)
        rows.extend(damping * np.eye(k * n))  # damping, as in damped least squares
        rhs.extend(np.zeros(k * n))
        step = np.linalg.lstsq(np.array(rows), np.array(rhs), rcond=None)[0]
        step = np.clip(step, -max_step, max_step).reshape(k, n)

        # Simple line search: keep the step length that lands closest to targets.
        best = None
        for alpha in (1.0, 0.5, 0.25):
            trial = np.clip(q + alpha * step, LIMITS[:, 0], LIMITS[:, 1])  # joint stops
            trial_error = np.sum(position_errors(trial, targets) ** 2)
            if best is None or trial_error < best[1]:
                best = (trial, trial_error)
        q, new_error = best
        history.append(q.copy())

        # Weight decay: shift priority to the targets once progress stalls.
        if error - new_error < 1e-3 * error:
            kappa, beta = 0.5 * kappa, 0.5 * beta
        error = new_error
        if np.sqrt(error / k) < 1e-4 and kappa < 1e-3:
            break
    return q, history


def stepwise_ik(targets, q_start, damping=0.05, iterations=200):
    """Baseline: damped pseudo-inverse IK, one target at a time, warm-started.

    It is the 'plain IK along the path' approach. It knows nothing about the
    obstacle or later targets, so its first configuration decides the rest.
    """
    q = q_start.copy()
    path = []
    for target in targets:
        for _ in range(iterations):
            tool = joint_points(q)[-1]
            jacobian = point_jacobian(q, tool, len(q) - 1)
            e = target - tool
            # Damped pseudo-inverse: J^T (J J^T + lambda^2 I)^-1 e
            dq = jacobian.T @ np.linalg.solve(jacobian @ jacobian.T + damping**2 * np.eye(2), e)
            q = np.clip(q + dq, LIMITS[:, 0], LIMITS[:, 1])
            if np.linalg.norm(e) < 1e-5:
                break
        path.append(q.copy())
    return np.array(path)


def wall_problem(k=10):
    """Targets down a vertical 'wall' line, an obstacle below, a straight start."""
    targets = np.column_stack((np.full(k, 0.55), np.linspace(0.40, -0.40, k)))
    obstacle = (0.30, -0.30, 0.10)  # x, y, radius (m)
    q_start = np.tile([0.0, 0.0, 0.0, 0.0], (k, 1))
    return targets, obstacle, q_start


def draw_arms(axes, q_all, targets, obstacle, title):
    axes.add_patch(Circle(obstacle[:2], obstacle[2], color="tab:red", alpha=0.3))
    axes.plot(targets[:, 0], targets[:, 1], "g.", markersize=6)
    for i, q in enumerate(q_all):
        points = joint_points(q)
        axes.plot(points[:, 0], points[:, 1], "-", color=str(0.1 + 0.6 * i / len(q_all)), linewidth=1.2)
    axes.set_aspect("equal")
    axes.set_xlim(-0.1, 0.9)
    axes.set_ylim(-0.6, 0.6)
    axes.set_title(title, fontsize=9)
    axes.tick_params(labelsize=7)


def run(save=None, show=False, kappa=1.0, use_obstacle=True):
    if not show:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    targets, obstacle, q_start = wall_problem()
    q_final, history = branch(targets, q_start, obstacle if use_obstacle else None, kappa=kappa)
    q_ik = stepwise_ik(targets, q_start[0])
    errors = np.linalg.norm(position_errors(q_final, targets), axis=1)
    print(f"Branching: {len(history) - 1} iterations, largest target error {errors.max():.1e} m, "
          f"smallest obstacle clearance {min(clearance(q, obstacle) for q in q_final):.3f} m")
    print(f"Stepwise IK: smallest obstacle clearance {min(clearance(q, obstacle) for q in q_ik):.3f} m "
          "(negative means a link passes through the obstacle)")

    figure = plt.figure(figsize=(12, 6.5))
    grid = figure.add_gridspec(2, 5)
    picks = np.unique(np.linspace(0, len(history) - 1, 5).astype(int))
    for column, p in enumerate(picks):
        draw_arms(figure.add_subplot(grid[0, column]), history[p], targets, obstacle, f"Branching, iteration {p}")
    draw_arms(figure.add_subplot(grid[1, 0]), q_ik, targets, obstacle, "Stepwise IK (baseline)")
    draw_arms(figure.add_subplot(grid[1, 1]), q_final, targets, obstacle, "Branching, final")
    angles = figure.add_subplot(grid[1, 2:5])
    for j in range(q_final.shape[1]):
        angles.plot(q_final[:, j], "o-", markersize=3, label=f"branching q{j + 1}")
        angles.plot(q_ik[:, j], "--", color=angles.lines[-1].get_color(), alpha=0.5)
    angles.set_xlabel("arm index along the path (dashed: stepwise IK)", fontsize=8)
    angles.set_ylabel("joint angle (rad)", fontsize=8)
    angles.legend(fontsize=7, ncol=2)
    angles.tick_params(labelsize=7)
    figure.tight_layout()
    if save:
        Path(save).parent.mkdir(parents=True, exist_ok=True)
        figure.savefig(save, dpi=140)
        print(f"Saved {save}")
    if show:
        plt.show()
    return q_final, q_ik


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--save", type=Path, help="save the figure to this image/PDF path")
    parser.add_argument("--show", action="store_true", help="open the figure window")
    parser.add_argument("--kappa", type=float, default=1.0, help="initial smoothness weight")
    parser.add_argument("--no-obstacle", action="store_true", help="branch without obstacle terms")
    args = parser.parse_args()
    run(args.save, args.show, args.kappa, not args.no_obstacle)
