"""Verify a temporary draft HW06 scaffold without expanding the release."""

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


class Homework06PreviewTests(unittest.TestCase):
    def test_temporary_student_tree_has_two_hw06_stubs_and_provided_geometry(self):
        files, report = prepare_release(ROOT)
        self.assertEqual(report["removed_solution_blocks"], 14)
        extra = [
            "src/intro_robotics/planning.py",
            "src/intro_robotics/rrt.py",
            "homework/hw06/__init__.py",
            "homework/hw06/README.md",
            "homework/hw06/scenes.py",
            "homework/hw06/visualization.py",
            "homework/hw06/hw06_planning.py",
            "tests/public/test_hw06_planning.py",
        ]
        self.assertTrue(all(name not in files for name in extra))
        for name in extra:
            data = (ROOT / name).read_bytes()
            if name.endswith(".py"):
                text, count = strip_solutions(data.decode("utf-8"), name)
                self.assertEqual(count, 2 if name.endswith("/rrt.py") else 0)
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
from intro_robotics.planning import edge_is_free
from intro_robotics.rrt import Tree, extend_tree, rrt_connect
from homework.hw06 import scenes
assert Path(intro_robotics.__file__).resolve().is_relative_to(Path.cwd() / 'src')
assert not edge_is_free([-0.2, 0], [0.2, 0], lambda q: abs(q[0]) > 0.05, 0.01)
def empty(call, label):
    try:
        call()
    except NotImplementedError as error:
        assert label in str(error), str(error)
    else:
        raise AssertionError('A HW06 answer remains in the preview')
empty(lambda: extend_tree(Tree([0, 0]), np.array([0.3, 0]), lambda q: True, 0.2, 0.02), 'HW06: implement extend_tree')
empty(lambda: rrt_connect([-0.8, 0], [0.8, 0], [[-1, 1], [-1, 1]], lambda q: True), 'HW06: implement rrt_connect')
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
