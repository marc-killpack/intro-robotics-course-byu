"""HW06 instructor master: a small, reversible two-tree planner.

The class and input checks are supplied. Students complete extend_tree and
the central rrt_connect loop; answer regions are removed in a student copy.
This draft is not in the current HW01--HW05 release manifest.
"""

import numpy as np

from intro_robotics.planning import check_rrt_inputs, edge_is_free


class Tree:
    """Configurations and parent indices; -1 marks the root's parent.

    points[i] is a configuration (n,) and parents[i] is the index of the node
    it was grown from.
    """

    def __init__(self, root):
        self.points = [np.array(root, dtype=float)]
        self.parents = [-1]

    def path_to(self, index):
        """Return configurations from this tree's root to the chosen node."""
        path = []
        while index != -1:
            path.append(self.points[index])
            index = self.parents[index]
        path.reverse()  # collected node -> root; return root -> node
        return path


def extend_tree(tree, target, is_free, step, resolution):
    """Try one extension; return (node_index, reached) or (None, False).

    tree: the Tree to grow.
    target: configuration (n,) to grow toward, same units as the tree points.
    is_free: function is_free(q) that returns True for a valid configuration.
    step: largest distance the new node may be from its nearest node.
    resolution: largest spacing between the checked configurations on the edge.

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
    # Move toward the target by at most one step.
    nearest_point = tree.points[nearest]
    fraction = min(step / distance, 1.0)
    candidate = nearest_point + fraction * (target - nearest_point)
    if not edge_is_free(nearest_point, candidate, is_free, resolution):
        return None, False
    tree.points.append(candidate)
    tree.parents.append(nearest)
    new_index = len(tree.points) - 1
    reached = fraction == 1.0
    return new_index, reached
    # END SOLUTION
    raise NotImplementedError("HW06: implement extend_tree")


def rrt_connect(start, goal, bounds, is_free, step=0.2, resolution=0.05, iterations=1000,
                seed=0):
    """Find a geometric start-to-goal path, or return None within the budget.

    start, goal: configurations (n,), for example meters for the base or
        radians for the arm joints.
    bounds: n-by-2 array; row i holds the [lower, upper] limits of coordinate i.
    is_free: function is_free(q) that returns True for a valid configuration.
    step: largest distance of one tree extension.
    resolution: largest spacing between checked configurations on an edge.
    iterations: number of samples to try before giving up.
    seed: random-number seed, so a run can be repeated.
    Returns a k-by-n array of configurations from start to goal, or None.

    Distances and interpolation are Euclidean; periodic angle wrapping is
    not modeled. Seeds allow repeatable class comparisons.
    """
    start, goal, bounds = check_rrt_inputs(start, goal, bounds, step, resolution, iterations)
    lower = bounds[:, 0]
    upper = bounds[:, 1]
    if np.any(start < lower) or np.any(start > upper):
        return None
    if np.any(goal < lower) or np.any(goal > upper):
        return None
    if not is_free(start) or not is_free(goal):
        return None
    if np.linalg.norm(start - goal) < 1e-12:
        return np.array([start])
    rng = np.random.default_rng(seed)

    # HW06: grow alternating trees, connect them, and return a start-to-goal
    # path without duplicating their meeting node. Return None on failure.
    # BEGIN SOLUTION
    start_tree = Tree(start)
    goal_tree = Tree(goal)
    grow_start_tree = True  # which tree takes the random step this attempt
    for iteration in range(iterations):
        if grow_start_tree:
            active = start_tree
            other = goal_tree
        else:
            active = goal_tree
            other = start_tree

        sample = rng.uniform(bounds[:, 0], bounds[:, 1])
        active_index, reached_sample = extend_tree(active, sample, is_free, step, resolution)
        if active_index is not None:
            # Grow the other tree toward the new node until it connects or is blocked.
            target = active.points[active_index]
            while True:
                other_index, reached = extend_tree(other, target, is_free, step, resolution)
                if other_index is None:
                    break
                if reached:
                    if grow_start_tree:
                        start_path = active.path_to(active_index)
                        goal_path = other.path_to(other_index)
                    else:
                        start_path = other.path_to(other_index)
                        goal_path = active.path_to(active_index)
                    # goal_path runs goal -> meeting node. Reverse it, and skip
                    # the meeting node, which already ends start_path.
                    goal_path.reverse()
                    path = start_path + goal_path[1:]
                    return np.array(path)
        grow_start_tree = not grow_start_tree
    return None
    # END SOLUTION
    raise NotImplementedError("HW06: implement rrt_connect")
