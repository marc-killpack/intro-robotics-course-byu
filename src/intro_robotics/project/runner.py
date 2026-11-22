"""Plain-Python lockstep runner: the graded way to run a controller.

Each control period: the simulator renders an observation, the command
computed one period earlier is applied for this period, and the controller
computes the next command from the new observation. Everything advances in
simulated time, so laptop speed cannot change a score.
"""

import time as wallclock

import numpy as np

from .contract import Command
from .simulator import SortingSimulator


class EpisodeResult:
    """The outcome of one episode.

    score: points (+10 sorted, -5 dropped or wrong bin).
    counts: {"sorted", "wrong_bin", "dropped", "missed", "failed_picks",
        "limit_hits", "collisions"} -> number of each.
    objects: number of objects in the episode.
    sim_time: simulated seconds when the episode ended.
    mean_step_ms, max_step_ms: controller compute time per step (wall clock), ms.
    trace: per-period record (run_episode with record=True), else empty.
    """

    def __init__(self, score, counts, objects, sim_time, mean_step_ms, max_step_ms, trace=None):
        if trace is None:
            trace = {}
        self.score = score
        self.counts = counts
        self.objects = objects
        self.sim_time = sim_time
        self.mean_step_ms = mean_step_ms
        self.max_step_ms = max_step_ms
        self.trace = trace

    def summary(self):
        """One line with the score, the counts, and the timing."""
        c = self.counts
        return (f"score {self.score} | sorted {c['sorted']}/{self.objects}, wrong bin "
                f"{c['wrong_bin']}, dropped {c['dropped']}, missed {c['missed']}, failed picks "
                f"{c['failed_picks']} | limit hits {c['limit_hits']}, collisions "
                f"{c['collisions']} | {self.sim_time:.2f} s simulated | controller "
                f"{self.mean_step_ms:.2f} ms mean, {self.max_step_ms:.2f} ms max per step")


def check_command(command, n):
    """Raise TypeError unless command is a Command with n joint velocities."""
    if not isinstance(command, Command) or command.dq.shape != (n,):
        raise TypeError(f"step() must return a Command with {n} joint velocities")


def run_episode(controller, simulator, render=True, record=False, watch=None):
    """Run one episode to completion and return an EpisodeResult.

    controller: a Controller built from the same scenario's Task.
    simulator: a fresh SortingSimulator (it holds the seed and the truth).
    render=False skips images (only for faculty controllers that use truth).
    record=True keeps a per-period trace of q, tool XY, phase, and objects.
    watch: optional function called as watch(obs, simulator) every period,
        for example to write video frames. It must not change anything.
    """
    if not isinstance(simulator, SortingSimulator):
        raise TypeError("run_episode needs a SortingSimulator")
    n = simulator.n
    controller.reset()
    pending = Command(np.zeros(n))  # what applies during the first period
    step_ms = []
    trace = {"time": [], "q": [], "tool": [], "phase": [], "objects": []}
    while not simulator.done:
        obs = simulator.observe(render=render)
        if watch is not None:
            watch(obs, simulator)
        start = wallclock.perf_counter()
        command = controller.step(obs)
        step_ms.append(1000 * (wallclock.perf_counter() - start))
        check_command(command, n)
        if record:
            objects = []
            for obj in simulator.objects:
                objects.append((obj.position.copy(), obj.state))
            trace["time"].append(simulator.time)
            trace["q"].append(simulator.q.copy())
            trace["tool"].append(simulator.tool_pose()[:3, 3].copy())
            trace["phase"].append(simulator.phase)
            trace["objects"].append(objects)
        simulator.advance_period(pending.dq, pending.request)
        pending = command  # one control period of delay

    if not record:
        trace = {}
    mean_step_ms = 0.0
    max_step_ms = 0.0
    if len(step_ms) > 0:
        mean_step_ms = float(np.mean(step_ms))
        max_step_ms = float(np.max(step_ms))
    return EpisodeResult(
        score=simulator.score,
        counts=dict(simulator.counts),
        objects=len(simulator.objects),
        sim_time=simulator.time,
        mean_step_ms=mean_step_ms,
        max_step_ms=max_step_ms,
        trace=trace,
    )
