"""Provided HW10 dataset: object crops from the project's fixed camera, with harder conditions.

Each *scene* is one object on the belt, seen by the fixed camera in FRAMES
consecutive frames (0.02 s apart) under one set of conditions:

- clean: the project's conditions with realism on (mild pixel noise).
- hard: what the project scenarios do not have yet, and fixed rules handle
  badly: brighter or darker light with a color cast, uneven light across
  the crop, blur, heavy noise, a dark bar partly covering the object, and
  crops that are not centered on the object.

Every crop is 48 x 48 RGB, centered (roughly) on one object, labeled with
its color and shape: 9 classes, CLASSES[label]. The crops of one scene are
nearly identical, so splits are made by scene, never by crop.

Generated in a few seconds from fixed seeds, so everyone has the same data.
"""

import copy
from pathlib import Path

import cv2
import numpy as np

from intro_robotics.project import load_scenario
from intro_robotics.project.scenario import make_cameras
from intro_robotics.project.simulator import SimObject, fill_polygons

SCENARIO = Path(__file__).resolve().parents[1] / "hw08" / "hw08_scenario.toml"  # the project camera and colors
COLORS = ("red", "blue", "yellow")
SHAPES = ("circle", "square", "triangle")
CLASSES = [f"{c} {s}" for c in COLORS for s in SHAPES]  # label = 3 * color index + shape index
CROP = 48  # pixels
FRAMES = 6  # crops per scene
SPLITS = {"train": (0, 2400), "val": (2400, 2700), "test": (2700, 3300)}  # scene numbers
HARD_FRACTION = 0.75  # of scenes in every split


def conditions(rng, hard):
    """One scene's imaging conditions."""
    if not hard:
        return dict(hard=False, gain=1.0, tint=np.ones(3), ramp=np.zeros(2), blur=0.0, noise=4.0,
                    occluder=None, jitter=1.5)
    return dict(hard=True, gain=rng.uniform(0.5, 1.5), tint=rng.uniform(0.85, 1.15, 3),
                ramp=rng.uniform(-0.4, 0.4, 2), blur=rng.uniform(0.0, 1.6), noise=rng.uniform(0.0, 20.0),
                occluder=rng.uniform(-1, 1, 2) if rng.random() < 0.35 else None, jitter=4.0)


def camera(rng):
    """The fixed camera, moved a few centimeters as between project scenarios."""
    scenario = copy.deepcopy(load_scenario(SCENARIO))
    c = scenario["cameras"]
    c["fixed_location"] = list(np.add(c["fixed_location"], rng.uniform(-0.04, 0.04, 3)))
    c["fixed_target"] = list(np.add(c["fixed_target"], rng.uniform(-0.03, 0.03, 3) * [1, 1, 0]))
    return make_cameras(scenario)[0], scenario


def apply_conditions(crop, cond, rng):
    """Lighting, color cast, uneven light, blur, then noise (uint8 in and out)."""
    image = crop.astype(np.float32) * cond["gain"] * cond["tint"]
    if np.any(cond["ramp"]):
        u, v = np.meshgrid(np.linspace(-1, 1, CROP), np.linspace(-1, 1, CROP))
        image *= (1 + cond["ramp"][0] * u + cond["ramp"][1] * v)[..., None]
    if cond["blur"] > 0.2:
        image = cv2.GaussianBlur(image, (0, 0), cond["blur"])
    image += rng.normal(0, cond["noise"], image.shape)
    return np.clip(np.rint(image), 0, 255).astype(np.uint8)


def make_scene(index):
    """Crops (FRAMES, CROP, CROP, 3) uint8, label, and conditions of scene `index` (deterministic)."""
    rng = np.random.default_rng(10_000 + index)
    hard = rng.random() < HARD_FRACTION
    cond = conditions(rng, hard)
    fixed, scenario = camera(rng)
    belt, colors = scenario["belt"], scenario["colors"]
    color, shape = rng.integers(3), rng.integers(3)
    obj = SimObject(COLORS[color], SHAPES[shape], np.array([rng.uniform(-0.3, 0.3), belt["y"] + rng.uniform(-0.04, 0.04)]),
                    size=rng.uniform(0.06, 0.08), yaw=rng.uniform(0, 2 * np.pi))
    belt_polygon = np.array([[belt["x_start"], belt["y"] - belt["width"] / 2], [belt["x_end"], belt["y"] - belt["width"] / 2],
                             [belt["x_end"], belt["y"] + belt["width"] / 2], [belt["x_start"], belt["y"] + belt["width"] / 2]])
    crops = []
    for frame in range(FRAMES):
        polygons, fills = [belt_polygon, obj.outline()], [[150, 150, 150], colors[obj.color]]
        if cond["occluder"] is not None:  # a dark bar (an arm link, a cable) fixed above the belt
            offset, angle = cond["occluder"] * [0.03, np.pi]
            along = np.array([np.cos(angle), np.sin(angle)])
            across = np.array([-along[1], along[0]])
            center = obj.position + offset * across
            polygons.append(np.array([center + s * 0.08 * along + w * 0.012 * across
                                      for s, w in ((-1, -1), (1, -1), (1, 1), (-1, 1))]))
            fills.append([70, 70, 70])
        image = fill_polygons(fixed, polygons, fills)
        u, v = fixed.project(np.array([[*obj.position, 0.0]]))[0][0] + rng.uniform(-1, 1, 2) * cond["jitter"]
        left, top = int(round(u - CROP / 2)), int(round(v - CROP / 2))
        crops.append(apply_conditions(image[top:top + CROP, left:left + CROP], cond, rng))
        obj.position = obj.position + [0.06 * 0.02, 0.0]  # the belt moves on
    return np.stack(crops), 3 * color + shape, cond


CACHE = Path("tmp/hw10")  # generated splits are saved here (about 40 MB) and reused


def load(split):
    """(images (N, 48, 48, 3) uint8 RGB, labels (N,), hard (N,) bool, scene (N,)) for one split.

    The first call generates the split (a few seconds) and saves it in CACHE.
    """
    path = CACHE / f"{split}.npz"
    if path.exists():
        with np.load(path) as data:
            if tuple(data["range"]) == SPLITS[split]:
                return data["images"], data["labels"], data["hard"], data["scene"]
    result = generate(split)
    CACHE.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, images=result[0], labels=result[1], hard=result[2], scene=result[3],
                        range=np.array(SPLITS[split]))
    return result


def generate(split):
    """Generate one split without the cache."""
    start, stop = SPLITS[split]
    images, labels, hard, scene = [], [], [], []
    for index in range(start, stop):
        crops, label, cond = make_scene(index)
        images.append(crops)
        labels += [label] * len(crops)
        hard += [cond["hard"]] * len(crops)
        scene += [index] * len(crops)
    return np.concatenate(images), np.array(labels), np.array(hard), np.array(scene)


def to_tensor(images):
    """Provided preprocessing: uint8 (N, H, W, 3) RGB -> float32 torch tensor (N, 3, H, W) in [0, 1]."""
    import torch

    return torch.from_numpy(np.ascontiguousarray(images.transpose(0, 3, 1, 2))).float() / 255.0
