"""Check a temporary cumulative HW06--HW07 student tree without publishing."""

import ast
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from release_tools.student_release import (
    ROOT,
    check_local_links,
    prepare_release,
    strip_solutions,
)


class Homework07PreviewTests(unittest.TestCase):
    def test_cumulative_preview_strips_planner_and_metric_answers(self):
        files, report = prepare_release(ROOT)
        self.assertEqual(report["removed_solution_blocks"], 11)
        extra = [
            "src/intro_robotics/planning.py",
            "src/intro_robotics/rrt.py",
            "src/intro_robotics/waypoint_optimization.py",
            "src/intro_robotics/waypoint_checks.py",
            "src/intro_robotics/waypoint_metrics.py",
            "homework/hw06/__init__.py",
            "homework/hw06/README.md",
            "homework/hw06/scenes.py",
            "homework/hw06/visualization.py",
            "homework/hw06/hw06_planning.py",
            "tests/public/test_hw06_planning.py",
            "homework/hw07/__init__.py",
            "homework/hw07/README.md",
            "homework/hw07/scenes.py",
            "homework/hw07/visualization.py",
            "homework/hw07/hw07_optimization.py",
            "tests/public/test_hw07_optimization.py",
        ]
        self.assertTrue(all(name not in files for name in extra))
        for name in extra:
            data = (ROOT / name).read_bytes()
            if name.endswith(".py"):
                text, count = strip_solutions(data.decode("utf-8"), name)
                expected = (
                    2 if name.endswith(("/rrt.py", "/waypoint_metrics.py")) else 0
                )
                self.assertEqual(count, expected)
                ast.parse(text, filename=name)
                data = text.encode("utf-8")
            files[name] = data
        check_local_links(files)

        with tempfile.TemporaryDirectory() as temporary:
            student = Path(temporary)
            for name, data in files.items():
                path = student / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
            environment = os.environ.copy()
            environment["PYTHONPATH"] = str(student / "src")
            probe = """
from pathlib import Path
import numpy as np
import intro_robotics
from intro_robotics.rrt import Tree, extend_tree
from intro_robotics.waypoint_metrics import path_length, smoothness_cost
import intro_robotics.waypoint_optimization as optimizer
from homework.hw07 import scenes
assert Path(intro_robotics.__file__).resolve().is_relative_to(Path.cwd() / 'src')
# Supply a temporary metric only inside this probe to isolate the provided solver.
optimizer.smoothness_cost = lambda path: float(np.sum(np.diff(path, n=2, axis=0) ** 2))
path, history = optimizer.optimize_waypoints([[-0.5, 0], [0, 0.2], [0.5, 0]], [[-1, 1], [-1, 1]], iterations=1)
assert path.shape == (3, 2) and len(history) >= 1
def empty(call, label):
    try:
        call()
    except NotImplementedError as error:
        assert label in str(error), str(error)
    else:
        raise AssertionError('A homework answer remains in the preview')
empty(lambda: extend_tree(Tree([0, 0]), np.array([0.3, 0]), lambda q: True, 0.2, 0.02), 'HW06')
empty(lambda: path_length([[0, 0], [1, 0]]), 'HW07: implement path_length')
empty(lambda: smoothness_cost([[0, 0], [1, 0], [2, 0]]), 'HW07: implement smoothness_cost')
"""
            result = subprocess.run(
                [sys.executable, "-c", probe],
                cwd=student,
                env=environment,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
