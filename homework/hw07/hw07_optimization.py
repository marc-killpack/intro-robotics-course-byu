"""Provided HW07 checks/viewer; implement metrics in waypoint_metrics.py."""

from homework.activity import run_activity


def build_scene():
    from homework.hw07.visualization import OptimizationView

    return OptimizationView()


if __name__ == "__main__":
    run_activity(7, build_scene)
