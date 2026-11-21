import ast
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from release_tools.student_release import (
    ROOT,
    prepare_release,
    safe_path,
    strip_solutions,
    write_release,
)


class ReleaseTests(unittest.TestCase):
    def test_malformed_markers_fail(self):
        for text in (
            "# END SOLUTION\n",
            "# BEGIN SOLUTION\nx=1\n",
            "# BEGIN SOLUTION\n# BEGIN SOLUTION\n",
        ):
            with self.subTest(text=text), self.assertRaises(ValueError):
                strip_solutions(text)

    def test_foundation_preview_has_labeled_stubs_and_no_project_modules(self):
        source = ROOT / "homework/hw01/joint_publisher.py"
        before = source.read_bytes()
        files, report = prepare_release(ROOT)
        self.assertEqual(report["removed_solution_blocks"], 14)
        self.assertEqual(
            files["homework/hw04/arm.urdf"],
            (ROOT / "homework/hw04/arm_starter.urdf").read_bytes(),
        )
        self.assertNotIn(b'name="joint2"', files["homework/hw04/arm.urdf"])
        text = files["homework/hw01/joint_publisher.py"].decode()
        self.assertNotIn("# BEGIN SOLUTION", text)
        self.assertNotIn("phase =", text)
        self.assertNotIn("self.publisher.publish(", text)
        tree = ast.parse(text)
        errors = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "NotImplementedError"
        ]
        self.assertEqual(len(errors), 2)
        self.assertFalse(
            any(
                name.startswith(
                    (
                        "instructor/",
                        "docs/homework/",
                        "tests/instructor/",
                        "examples/",
                        "homework/hw08/",
                    )
                )
                for name in files
            )
        )
        self.assertEqual(before, source.read_bytes())
        self.assertIn(b"HW01", files["README.md"])
        for name in (
            "camera",
            "vision",
            "planning",
            "rrt",
            "planar_scene",
            "waypoint_optimization",
            "waypoint_checks",
            "waypoint_metrics",
        ):
            self.assertNotIn(f"src/intro_robotics/{name}.py", files)
        self.assertIn("tests/public/test_hw05_planar_jacobian.py", files)
        # The project package (and its faculty oracle) waits for its own release.
        self.assertFalse(any(name.startswith(("src/intro_robotics/project/", "homework/project/"))
                             for name in files))

    def test_generated_package_imports_and_all_nine_future_methods_stay_empty(self):
        with tempfile.TemporaryDirectory() as temporary:
            student = Path(temporary) / "student"
            write_release(ROOT, student, allow_dirty=True)
            environment = os.environ.copy()
            environment["PYTHONPATH"] = str(student / "src")
            environment["MPLBACKEND"] = "Agg"
            probe = """
from pathlib import Path
import importlib
import pkgutil
import numpy as np
import intro_robotics
from intro_robotics import Joint, SerialArm
from intro_robotics import transforms as t
from intro_robotics.visualization import VizScene
from intro_robotics.visualization_3d import ArmMeshObject
assert Path(intro_robotics.__file__).resolve().is_relative_to(Path.cwd() / 'src')
for module in pkgutil.walk_packages(intro_robotics.__path__, 'intro_robotics.'):
    importlib.import_module(module.name)
for name in ('camera', 'vision', 'planning', 'rrt', 'planar_scene', 'waypoint_optimization', 'waypoint_checks', 'waypoint_metrics'):
    assert importlib.util.find_spec('intro_robotics.' + name) is None
def empty(function, arguments, label):
    try:
        function(*arguments)
    except NotImplementedError as error:
        assert label in str(error), str(error)
    else:
        raise AssertionError('Assigned answer remains: ' + label)
for name in ('rot2', 'rotx', 'roty', 'rotz'):
    empty(getattr(t, name), [0.2], 'HW02')
empty(t.rot_inv, [np.eye(3)], 'HW02')
empty(t.se3, [], 'HW03')
empty(t.inv, [np.eye(4)], 'HW03')
arm = SerialArm([Joint()])
empty(arm.fk, [[0]], 'HW04')
empty(lambda: ArmMeshObject(arm, q0=[0]), [], 'HW04')
# Isolate the HW05 placeholder from its still-unfinished HW04 prerequisite.
arm.fk = lambda *args, **kwargs: np.eye(4)
empty(arm.jacob_planar, [[0]], 'HW05')
from intro_robotics.kinematics import damped_least_squares
empty(damped_least_squares, [np.eye(2), [0.0, 0.0]], 'HW06')
empty(arm.ik_position, [[0.0, 0.0], [0.0]], 'HW06')
from homework.hw03.frame_broadcaster import frame_transforms
empty(frame_transforms, [], 'HW03')
scene = VizScene()
scene.add_frame(np.eye(4), 'W')
scene.update(As=[np.eye(4)])
scene.fig.canvas.draw()
"""
            result = subprocess.run(
                [os.sys.executable, "-c", probe],
                cwd=student,
                env=environment,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_traversal_is_rejected(self):
        with self.assertRaises(ValueError):
            safe_path(ROOT, "../outside.txt")

    def test_clean_copy_nonoverwrite_and_dirty_gate(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "source"
            root.mkdir()
            (root / "release_tools").mkdir()
            manifest = {"scope": "fixture", "files": {"master.py": "task.py"}}
            (root / "release_tools/release_manifest.json").write_text(
                json.dumps(manifest)
            )
            master = "def answer():\n    # BEGIN SOLUTION\n    return 12345\n    # END SOLUTION\n    raise NotImplementedError('HW01')\n"
            (root / "master.py").write_text(master)
            for args in (
                ["init", "-q"],
                ["add", "."],
                [
                    "-c",
                    "user.name=Release Test",
                    "-c",
                    "user.email=release-test@example.invalid",
                    "commit",
                    "-qm",
                    "fixture",
                ],
            ):
                subprocess.run(
                    ["git", "-C", str(root), *args], check=True, capture_output=True
                )
            destination = Path(temporary) / "student"
            report = write_release(root, destination)
            self.assertFalse(report["source_dirty"])
            self.assertNotIn("12345", (destination / "task.py").read_text())
            self.assertEqual((root / "master.py").read_text(), master)
            with self.assertRaises(FileExistsError):
                write_release(root, destination)
            (root / "master.py").write_text(master + "# changed\n")
            with self.assertRaisesRegex(ValueError, "commit"):
                write_release(root, Path(temporary) / "another")
            self.assertFalse((Path(temporary) / "another").exists())


if __name__ == "__main__":
    unittest.main()
