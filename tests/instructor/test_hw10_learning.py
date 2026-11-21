"""Faculty checks for HW10 (the data, the rule-versus-network gap, training, and stubs)."""

from pathlib import Path
import runpy
import tempfile
import unittest

import numpy as np
from numpy.testing import assert_array_equal

from homework.hw10.dataset import CLASSES, SPLITS, load, make_scene
from homework.hw10.hw10_evaluate import SUPPLIED, evaluate
from homework.hw10.hw10_train import train
from release_tools.student_release import strip_solutions

ROOT = Path(__file__).resolve().parents[2]


class DataTests(unittest.TestCase):
    def test_scenes_are_repeatable_and_splits_disjoint(self):
        a, b = make_scene(5), make_scene(5)
        assert_array_equal(a[0], b[0])
        self.assertEqual(a[1], b[1])
        ranges = sorted(SPLITS.values())
        self.assertTrue(all(r[1] <= s[0] for r, s in zip(ranges, ranges[1:])))
        _, labels, hard, scene = load("test")
        self.assertEqual(set(labels.tolist()), set(range(len(CLASSES))))
        self.assertTrue(0.65 < hard.mean() < 0.85)
        self.assertEqual(len(set(scene.tolist())), SPLITS["test"][1] - SPLITS["test"][0])


class GapTests(unittest.TestCase):
    """Learning has to matter: rules hold on clean crops and fail on hard ones; the network holds on both."""

    def test_supplied_checkpoint_against_the_rules(self):
        r = evaluate(SUPPLIED)
        clean, hard = ~r["hard"], r["hard"]
        accuracy = lambda name, m: (r[name][m] == r["labels"][m]).mean()  # noqa: E731
        self.assertGreater(accuracy("rule", clean), 0.98)
        self.assertLess(accuracy("rule", hard), 0.6)
        self.assertGreater(accuracy("network", clean), 0.98)
        self.assertGreater(accuracy("network", hard), 0.95)

    def test_one_epoch_with_the_key_learns(self):
        _, history = train(epochs=1, seed=3, log=lambda line: None)
        epoch, loss, seconds, clean, hard = history[0]
        self.assertLess(loss, 1.2)
        self.assertGreater(clean, 0.85)
        self.assertGreater(hard, 0.6)


class StubTests(unittest.TestCase):
    def test_stripped_file_has_three_labeled_stubs(self):
        source = (ROOT / "homework/hw10/learning.py").read_text()
        stripped = strip_solutions(source)
        stripped = stripped if isinstance(stripped, str) else stripped[0]
        self.assertEqual(source.count("# BEGIN SOLUTION"), 3)
        self.assertNotIn("loss.backward()", stripped)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "learning.py"
            path.write_text(stripped)
            namespace = runpy.run_path(str(path))
        import torch

        model = torch.nn.Sequential(torch.nn.Flatten(), torch.nn.Linear(4, 2))
        x, y = torch.zeros(4, 1, 2, 2), torch.zeros(4, dtype=torch.long)
        calls = {
            "train_epoch": (model, [(x, y)], torch.optim.SGD(model.parameters(), lr=0.1), torch.nn.CrossEntropyLoss()),
            "predict": (model, x),
            "confusion_matrix": ([0], [0], 2),
        }
        for name, arguments in calls.items():
            with self.subTest(function=name), self.assertRaisesRegex(NotImplementedError, "HW10"):
                namespace[name](*arguments)


if __name__ == "__main__":
    unittest.main()
