"""Plain-Python lockstep runner: the graded way to run a controller.

Each control period: the simulator renders an observation, the command
computed one period earlier is applied for this period, and the controller
computes the next command from the new observation. Everything advances in
simulated time, so laptop speed cannot change a score.
"""

from dataclasses import dataclass, field
import time as wallclock

import numpy as np

from .contract import Command
from .simulator import SortingSimulator


@dataclass
class EpisodeResult:
    score: int
    counts: dict
    objects: int
    sim_time: float
    mean_step_ms: float  # controller compute time per step (wall clock)
    max_step_ms: float
    trace: dict = field(default_factory=dict)

    def summary(self):
        c = self.counts
        return (f"score {self.score} | sorted {c['sorted']}/{self.objects}, wrong bin "
                f"{c['wrong_bin']}, dropped {c['dropped']}, missed {c['missed']}, failed picks "
                f"{c['failed_picks']} | limit hits {c['limit_hits']}, collisions "
                f"{c['collisions']} | {self.sim_time:.2f} s simulated | controller "
                f"{self.mean_step_ms:.2f} ms mean, {self.max_step_ms:.2f} ms max per step")


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
        if not isinstance(command, Command) or command.dq.shape != (n,):
            raise TypeError(f"step() must return a Command with {n} joint velocities")
        if record:
            trace["time"].append(simulator.time)
            trace["q"].append(simulator.q.copy())
            trace["tool"].append(simulator.tool_pose()[:3, 3].copy())
            trace["phase"].append(simulator.phase)
            trace["objects"].append([(o.position.copy(), o.state) for o in simulator.objects])
        simulator.advance_period(pending.dq, pending.request)
        pending = command  # one control period of delay
    return EpisodeResult(
        score=simulator.score,
        counts=dict(simulator.counts),
        objects=len(simulator.objects),
        sim_time=simulator.time,
        mean_step_ms=float(np.mean(step_ms)) if step_ms else 0.0,
        max_step_ms=float(np.max(step_ms)) if step_ms else 0.0,
        trace=trace if record else {},
    )
