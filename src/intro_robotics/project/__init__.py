"""Conveyor-sorting project: student contract, simulator, and lockstep runner.

Students write a Controller subclass (contract.py). The supplied simulator
and runner step it in simulated time; the same class will later run inside a
ROS 2 node. Distances are meters, angles radians, and times seconds.
"""

from .contract import Command, Controller, Observation, Task
from .runner import EpisodeResult, run_episode
from .scenario import load_scenario
from .simulator import SortingSimulator

__all__ = [
    "Command",
    "Controller",
    "EpisodeResult",
    "Observation",
    "SortingSimulator",
    "Task",
    "load_scenario",
    "run_episode",
]
