"""Provided command-line/check setup so activity files stay short."""

import argparse
from pathlib import Path
import unittest


def run_activity(number, build_scene):
    parser = argparse.ArgumentParser(
        description=f"HW{number:02d}: limited checks and optional visualization"
    )
    parser.add_argument(
        "--show", action="store_true", help="open the supplied visualization"
    )
    parser.add_argument(
        "--save", type=Path, help="save the visualization to this image/PDF path"
    )
    args = parser.parse_args()
    suite = unittest.defaultTestLoader.discover(
        "tests/public", pattern=f"test_hw{number:02d}_*.py"
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)
    if args.show or args.save:
        scene = build_scene()
        if args.save:
            args.save.parent.mkdir(parents=True, exist_ok=True)
            scene.fig.savefig(args.save, dpi=140)
        if args.show:
            scene.show()
