import ast
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from release_tools.student_release import (
    ROOT,
    check_local_links,
    heading_anchors,
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
        with self.assertRaises(ValueError):
            strip_solutions("<!-- BEGIN FACULTY ONLY -->\nplan\n", "AGENTS.md",
                            "<!-- BEGIN FACULTY ONLY -->", "<!-- END FACULTY ONLY -->")

    def test_release_has_labeled_stubs_and_no_faculty_keys(self):
        source = ROOT / "homework/hw01/joint_publisher.py"
        before = source.read_bytes()
        files, report = prepare_release(ROOT)
        # HW01-HW05: 14 (two HW06 stubs live in kinematics.py); HW06 rrt 2;
        # HW07 4; vision.py 7 (six HW08 and the project's find_board_corners);
        # HW09 2; HW10 3; HW11 4.
        self.assertEqual(report["removed_solution_blocks"], 36)
        # AGENTS.md keeps its tutoring rules but loses the faculty planning paragraph.
        self.assertEqual(report["removed_faculty_markdown_blocks"], 1)
        agents = files["AGENTS.md"].decode()
        self.assertIn("Never complete an assigned", agents)
        self.assertNotIn("faculty task list", agents)
        self.assertNotIn("FACULTY", agents)
        self.assertIn(b"faculty task list", (ROOT / "AGENTS.md").read_bytes())
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
                    )
                )
                for name in files
            )
        )
        self.assertEqual(before, source.read_bytes())
        self.assertIn(b"HW01", files["README.md"])
        # Faculty answers and truth-based controllers are never released.
        for name in (
            "homework/hw07/planar_arm.urdf",
            "src/intro_robotics/project/reference.py",
            "src/intro_robotics/project/oracle.py",
            "src/intro_robotics/planar_scene.py",
        ):
            self.assertNotIn(name, files)
        for name in (
            "tests/public/test_hw05_planar_jacobian.py",
            "tests/public/test_hw11_rewards.py",
            "homework/project/my_controller.py",
            "student_ws/ros2_ws/src/conveyor_interfaces/msg/PickupRequest.msg",
        ):
            self.assertIn(name, files)
        for name in ("src/intro_robotics/vision.py", "homework/hw09/ibvs_controller.py",
                     "homework/hw10/learning.py", "homework/hw11/rewards.py"):
            self.assertIn(b"NotImplementedError", files[name])
        self.assertNotIn(b"findHomography(np", files["src/intro_robotics/vision.py"])
        self.assertNotIn(b"camera_velocity =", files["homework/hw09/ibvs_controller.py"])
        self.assertNotIn(b"loss.backward()", files["homework/hw10/learning.py"])

    def test_generated_package_imports_and_assigned_methods_stay_empty(self):
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
for name in ('planar_scene', 'project.reference', 'project.oracle'):
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
from intro_robotics import vision
empty(vision.to_plane, [np.eye(3), (0, 0)], 'HW08')
empty(vision.fit_velocity, [[0, 1], [[0, 0], [1, 0]]], 'HW08')
empty(vision.find_board_corners, [np.zeros((4, 4, 3), np.uint8), {'squares': (3, 3)}], 'Project')
from homework.hw09.ibvs_controller import ibvs_velocity
empty(ibvs_velocity, [(0, 0), (1, 1), 0.3, 300.0, 0.0, 2.0], 'HW09')
from homework.hw11.rewards import sparse_reward
empty(sparse_reward, [{'success': False}], 'HW11')
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

    def test_heading_anchors_follow_github_rules(self):
        text = (
            "# Python on your own computer (HW02--HW05)\n"
            "## Two places to run commands\n"
            "## Notes\n"
            "## Notes\n"
            "```text\n# not a heading\n```\n"
            '<a id="custom-spot"></a>\n'
        )
        self.assertEqual(
            heading_anchors(text),
            {
                "python-on-your-own-computer-hw02--hw05",
                "two-places-to-run-commands",
                "notes",
                "notes-1",
                "custom-spot",
            },
        )

    def test_section_links_are_checked(self):
        setup = b"# Setup\n## Two places to run commands\n"
        good = {
            "docs/setup.md": setup,
            "GUIDE.md": b"[ok](docs/setup.md#two-places-to-run-commands) [top](#guide)\n# Guide\n",
        }
        check_local_links(good)
        for link in ("docs/setup.md#three-places", "#missing"):
            files = {"docs/setup.md": setup, "GUIDE.md": f"# Guide\n[bad]({link})\n".encode()}
            with self.subTest(link=link), self.assertRaises(ValueError):
                check_local_links(files)

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
