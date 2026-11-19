"""HW06 instructor master: a small, reversible two-tree planner.

The class and input checks are supplied. Students complete extend_tree and
the central rrt_connect loop; answer regions are removed in a student copy.
This draft is not in the current HW01--HW05 release manifest.
"""

import numpy as np

from intro_robotics.planning import check_rrt_inputs, edge_is_free


class Tree:
    """Configurations and parent indices; -1 marks the root's parent."""

    def __init__(self, root):
        self.points = [np.array(root, dtype=float)]
        self.parents = [-1]

    def path_to(self, index):
        """Return configurations from this tree's root to the chosen node."""
        path = []
        while index != -1:
            path.append(self.points[index])
            index = self.parents[index]
        return path[::-1]


def extend_tree(tree, target, is_free, step, resolution):
    """Try one extension; return (node_index, reached) or (None, False).

    Use the nearest node and step toward target by at most step. Check the
    entire candidate edge. Record the parent only when the edge is valid.
    If the target is already a node, return that existing node and True.
    """
    # HW06: find the nearest node, steer, check the edge, and record a node.
    # BEGIN SOLUTION
    distances = [np.linalg.norm(point - target) for point in tree.points]
    nearest = int(np.argmin(distances))
    distance = distances[nearest]
    if distance < 1e-12:
        return nearest, True
    fraction = min(step / distance, 1.0)
    candidate = tree.points[nearest] + fraction * (target - tree.points[nearest])
    if not edge_is_free(tree.points[nearest], candidate, is_free, resolution):
        return None, False
    tree.points.append(candidate)
    tree.parents.append(nearest)
    return len(tree.points) - 1, fraction == 1.0
    # END SOLUTION
    raise NotImplementedError("HW06: implement extend_tree")


def rrt_connect(
    start, goal, bounds, is_free, *, step=0.2, resolution=0.05, iterations=1000, seed=0
):
    """Find a geometric start-to-goal path, or return None within the budget.

    ``bounds`` is an n-by-2 array and ``is_free(q)`` tests configurations.
    Distances and interpolation are Euclidean; periodic angle wrapping is
    not modeled. Seeds allow repeatable class comparisons.
    """
    start, goal, bounds = check_rrt_inputs(
        start, goal, bounds, step, resolution, iterations
    )
    if (
        np.any(start < bounds[:, 0])
        or np.any(start > bounds[:, 1])
        or np.any(goal < bounds[:, 0])
        or np.any(goal > bounds[:, 1])
    ):
        return None
    if not is_free(start) or not is_free(goal):
        return None
    if np.linalg.norm(start - goal) < 1e-12:
        return np.array([start])
    rng = np.random.default_rng(seed)

    # HW06: grow alternating trees, connect them, and return a start-to-goal
    # path without duplicating their meeting node. Return None on failure.
    # BEGIN SOLUTION
    start_tree, goal_tree = Tree(start), Tree(goal)
    active, other, active_is_start = start_tree, goal_tree, True
    for _ in range(iterations):
        sample = rng.uniform(bounds[:, 0], bounds[:, 1])
        active_index, _ = extend_tree(active, sample, is_free, step, resolution)
        if active_index is not None:
            target = active.points[active_index]
            while True:
                other_index, reached = extend_tree(
                    other, target, is_free, step, resolution
                )
                if other_index is None:
                    break
                if reached:
                    if active_is_start:
                        first, second = active.path_to(active_index), other.path_to(
                            other_index
                        )
                    else:
                        first, second = other.path_to(other_index), active.path_to(
                            active_index
                        )
                    return np.asarray(first + second[-2::-1])
        active, other = other, active
        active_is_start = not active_is_start
    return None
    # END SOLUTION
    raise NotImplementedError("HW06: implement rrt_connect")
