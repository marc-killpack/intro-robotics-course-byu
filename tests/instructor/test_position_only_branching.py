"""Faculty checks for the lecture P6 branching example (D9)."""

import unittest

import numpy as np
from numpy.testing import assert_allclose

from examples.position_only_branching import (
    LIMITS,
    LINKS,
    branch,
    clearance,
    joint_points,
    point_jacobian,
    position_errors,
    stepwise_ik,
    wall_problem,
)
from intro_robotics import Joint, SerialArm
from intro_robotics.transforms import se3


class BranchingExample(unittest.TestCase):
    def test_tool_jacobian_matches_jacob_planar(self):
        arm = SerialArm([Joint("z", tip=se3(translation=[length, 0, 0])) for length in LINKS])
        q = np.array([0.4, -0.7, 1.1, 0.3])
        tool = joint_points(q)[-1]
        assert_allclose(tool, arm.fk(q)[:2, 3], atol=1e-12)
        assert_allclose(point_jacobian(q, tool, 3), arm.jacob_planar(q)[:2], atol=1e-12)

    def test_branching_reaches_targets_within_limits_and_clear_of_obstacle(self):
        targets, obstacle, q_start = wall_problem()
        q_final, history = branch(targets, q_start, obstacle)
        self.assertLess(np.linalg.norm(position_errors(q_final, targets), axis=1).max(), 1e-3)
        self.assertTrue(np.all(q_final >= LIMITS[:, 0]) and np.all(q_final <= LIMITS[:, 1]))
        self.assertGreater(min(clearance(q, obstacle) for q in q_final), 0.0)
        # Neighboring configurations stay close: the motion is smooth.
        self.assertLess(np.abs(np.diff(q_final, axis=0)).max(), 0.6)
        self.assertLess(len(history), 400)

    def test_qp_step_respects_stops_and_never_costs_more_than_clipping(self):
        # One iteration's subproblem with tight stops: the QP optimizes inside
        # the limits; least squares then clipping is merely feasible.
        from examples.position_only_branching import solve_step

        rng = np.random.default_rng(5)
        limits = np.array([[-1.0, 1.0]] * 4)
        q = rng.uniform(-0.95, 0.95, (3, 4))
        A, b = rng.normal(size=(30, 12)), rng.normal(size=30)
        qp = solve_step(A, b, q, limits, 0.15, "qp")
        clipped = np.clip(solve_step(A, b, q, limits, 0.15, "lstsq"), limits[0, 0] - q.ravel(),
                          limits[0, 1] - q.ravel())
        new_q = q.ravel() + qp
        self.assertTrue(np.all(new_q >= -1 - 1e-9) and np.all(new_q <= 1 + 1e-9))
        self.assertTrue(np.all(np.abs(qp) <= 0.15 + 1e-9))
        cost = lambda step: np.sum((A @ step - b) ** 2)
        self.assertLessEqual(cost(qp), cost(clipped) + 1e-9)

    def test_both_solvers_solve_the_default_problem(self):
        # The arm is redundant, so the two may settle on different (equally
        # good) joint paths; both must reach, stay smooth, and clear.
        targets, obstacle, q_start = wall_problem()
        for solver in ("qp", "lstsq"):
            q, _ = branch(targets, q_start, obstacle, solver=solver)
            self.assertLess(np.linalg.norm(position_errors(q, targets), axis=1).max(), 1e-3)
            self.assertGreater(min(clearance(c, obstacle) for c in q), 0.0)
            self.assertLess(np.abs(np.diff(q, axis=0)).max(), 0.6)

    def test_stepwise_ik_baseline_still_hits_the_obstacle(self):
        # The lecture contrast depends on this; retune wall_problem if it changes.
        targets, obstacle, q_start = wall_problem()
        q_ik = stepwise_ik(targets, q_start[0])
        self.assertLess(np.linalg.norm(position_errors(q_ik, targets), axis=1).max(), 1e-3)
        self.assertLess(min(clearance(q, obstacle) for q in q_ik), 0.0)


if __name__ == "__main__":
    unittest.main()
