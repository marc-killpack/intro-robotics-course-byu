"""Faculty-only oracle controller: sees object truth, obeys the same limits.

It estimates what is physically achievable under the simulator's limits,
delay, and actuator timing (the denominator for the 70-80% pass level). It
is not in the student release and must never be used to grade a student.
Same delay, limits, and pickup rules as a student; only its knowledge differs.
"""

import numpy as np

from .contract import Command, Controller


def damped_solve(jacobian, velocity, damping=0.05):
    """Damped least squares: dq = J^T (J J^T + damping^2 I)^-1 v."""
    jjt = jacobian @ jacobian.T
    return jacobian.T @ np.linalg.solve(jjt + damping**2 * np.eye(len(jjt)), velocity)


class OracleController(Controller):
    """Track the most downstream object, pick it, and carry it to its bin."""

    def __init__(self, task, simulator, gain=5.0, max_speed=0.8, posture_gain=1.0):
        super().__init__(task)
        self.sim = simulator  # privileged access to object truth
        self.gain, self.max_speed, self.posture_gain = gain, max_speed, posture_gain
        self.posture = np.array([0.6, 0.9, 0.9, 0.6])  # a smooth C shape, no folding
        self.target = None

    def reset(self):
        self.target = None

    def _choose_object(self, tool):
        reach = 0.92 * self.sim.lengths.sum()
        base = self.sim.base_xy
        candidates = [o for o in self.sim.objects if o.state == "belt"
                      and np.linalg.norm(o.position - base) < reach
                      and o.position[0] < self.task.belt["x_end"] - 0.05]
        # Most downstream first; it leaves the belt soonest.
        return max(candidates, key=lambda o: o.position[0]) if candidates else None

    def step(self, obs):
        period = self.task.control_period
        tool, jacobian = self.sim.tool_xy_and_jacobian(obs.q)
        tool_velocity = jacobian @ obs.dq
        belt_velocity = np.array([self.sim.belt_speed, 0.0])
        request = "hold"

        if obs.actuator in ("idle", "lowering"):
            if obs.actuator == "idle" or self.target is None or self.target.state != "belt":
                self.target = self._choose_object(tool)
            if self.target is None:
                goal, feedforward = tool, np.zeros(2)
            else:
                # Lead the object by the two-period command delay.
                goal = self.target.position + belt_velocity * 2 * period
                feedforward = belt_velocity
                close = np.linalg.norm(goal - tool) < 0.008
                matched = np.linalg.norm(tool_velocity - belt_velocity) < 0.03
                if obs.actuator == "idle" and close and matched:
                    request = "pick"
        elif obs.actuator == "holding" and self.sim.held is not None:
            held = self.sim.held
            x, y, _ = self.task.bins[self.task.rules[(held.color, held.shape)]]
            goal, feedforward = np.array([x, y]), np.zeros(2)
            if np.linalg.norm(goal - tool) < 0.02 and np.linalg.norm(tool_velocity) < 0.05:
                request = "release"
        else:  # lifting or releasing: keep still over the spot
            goal, feedforward = tool, np.zeros(2)
            if obs.actuator == "lifting" and self.sim.held is None:
                goal, feedforward = tool, np.zeros(2)

        velocity = feedforward + self.gain * (goal - tool)
        speed = np.linalg.norm(velocity)
        if speed > self.max_speed:
            velocity *= self.max_speed / speed
        dq = damped_solve(jacobian, velocity)
        # Null-space posture term keeps the redundant arm unfolded.
        null = np.eye(len(obs.q)) - np.linalg.pinv(jacobian) @ jacobian
        dq += null @ (self.posture_gain * (self.posture - obs.q))
        return Command(dq, request)


def achievable(scenario, seeds, render=False):
    """Run the oracle on each seed; return the EpisodeResults (faculty use)."""
    from .runner import run_episode
    from .scenario import make_task
    from .simulator import SortingSimulator

    results = []
    for seed in seeds:
        simulator = SortingSimulator(scenario, seed=seed)
        results.append(run_episode(OracleController(make_task(scenario), simulator),
                                   simulator, render=render))
    return results


if __name__ == "__main__":
    import argparse

    from .scenario import load_scenario

    parser = argparse.ArgumentParser(description="Faculty: oracle score per seed")
    parser.add_argument("--scenario", default="s1")
    parser.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3])
    args = parser.parse_args()
    for seed, result in zip(args.seeds, achievable(load_scenario(args.scenario), args.seeds)):
        print(f"seed {seed}: {result.summary()}")
