"""Provided HW06 checks/viewer; implement the planner in intro_robotics.rrt."""

from homework.activity import run_activity


def build_scene():
    from homework.hw06.visualization import PlanningView

    return PlanningView()


if __name__ == "__main__":
    run_activity(6, build_scene)
