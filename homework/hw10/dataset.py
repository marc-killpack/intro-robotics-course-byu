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
import torch

from intro_robotics.project import load_scenario
from intro_robotics.project.scenario import make_cameras
from intro_robotics.project.simulator import SimObject, fill_polygons

SCENARIO = Path(__file__).resolve().parents[1] / "hw08" / "hw08_scenario.toml"  # the project camera and colors
COLORS = ("red", "blue", "yellow")
SHAPES = ("circle", "square", "triangle")
# label = 3 * color index + shape index
CLASSES = ["red circle", "red square", "red triangle",
           "blue circle", "blue square", "blue triangle",
           "yellow circle", "yellow square", "yellow triangle"]
CROP = 48  # pixels
FRAMES = 6  # crops per scene
SPLITS = {"train": (0, 2400), "val": (2400, 2700), "test": (2700, 3300)}  # scene numbers
HARD_FRACTION = 0.75  # of scenes in every split
CACHE = Path("tmp/hw10")  # generated splits are saved here (about 40 MB) and reused


def conditions(rng, hard):
    """One scene's imaging conditions, as a dictionary."""
    if not hard:
        return {"hard": False, "gain": 1.0, "tint": np.ones(3), "ramp": np.zeros(2),
                "blur": 0.0, "noise": 4.0, "occluder": None, "jitter": 1.5}
    gain = rng.uniform(0.5, 1.5)  # overall brightness
    tint = rng.uniform(0.85, 1.15, 3)  # color cast: one factor per R, G, B
    ramp = rng.uniform(-0.4, 0.4, 2)  # uneven light: change across the crop in u and v
    blur = rng.uniform(0.0, 1.6)  # pixels
    noise = rng.uniform(0.0, 20.0)  # standard deviation, gray levels
    occluder = None  # a dark bar over the object, in about a third of the scenes
    if rng.random() < 0.35:
        occluder = rng.uniform(-1, 1, 2)  # its offset and angle, scaled to [-1, 1]
    return {"hard": True, "gain": gain, "tint": tint, "ramp": ramp, "blur": blur,
            "noise": noise, "occluder": occluder, "jitter": 4.0}


def camera(rng):
    """The fixed camera, moved a few centimeters as between project scenarios."""
    scenario = copy.deepcopy(load_scenario(SCENARIO))
    cameras = scenario["cameras"]
    location_change = rng.uniform(-0.04, 0.04, 3)
    cameras["fixed_location"] = list(np.add(cameras["fixed_location"], location_change))
    target_change = rng.uniform(-0.03, 0.03, 3) * [1, 1, 0]  # the target stays on the belt
    cameras["fixed_target"] = list(np.add(cameras["fixed_target"], target_change))
    fixed = make_cameras(scenario)[0]
    return fixed, scenario


def apply_conditions(crop, cond, rng):
    """Lighting, color cast, uneven light, blur, then noise (uint8 in and out)."""
    image = crop.astype(np.float32) * cond["gain"] * cond["tint"]
    if np.any(cond["ramp"]):
        u, v = np.meshgrid(np.linspace(-1, 1, CROP), np.linspace(-1, 1, CROP))  # -1 to 1 across the crop
        brightness = 1 + cond["ramp"][0] * u + cond["ramp"][1] * v
        image *= brightness[:, :, None]  # the same factor for all three colors
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
    belt = scenario["belt"]
    colors = scenario["colors"]
    color = rng.integers(3)
    shape = rng.integers(3)
    x = rng.uniform(-0.3, 0.3)
    y = belt["y"] + rng.uniform(-0.04, 0.04)
    obj = SimObject(COLORS[color], SHAPES[shape], np.array([x, y]),
                    size=rng.uniform(0.06, 0.08), yaw=rng.uniform(0, 2 * np.pi))
    belt_low = belt["y"] - belt["width"] / 2  # belt edges, world y
    belt_high = belt["y"] + belt["width"] / 2
    belt_polygon = np.array([[belt["x_start"], belt_low], [belt["x_end"], belt_low],
                             [belt["x_end"], belt_high], [belt["x_start"], belt_high]])
    crops = []
    for frame in range(FRAMES):
        polygons = [belt_polygon, obj.outline()]
        fills = [[150, 150, 150], colors[obj.color]]
        if cond["occluder"] is not None:  # a dark bar (an arm link, a cable) fixed above the belt
            offset = cond["occluder"][0] * 0.03  # meters across the bar from the object's center
            angle = cond["occluder"][1] * np.pi
            along = np.array([np.cos(angle), np.sin(angle)])
            across = np.array([-along[1], along[0]])
            center = obj.position + offset * across
            half_length = 0.08 * along
            half_width = 0.012 * across
            bar = np.array([center - half_length - half_width,
                            center + half_length - half_width,
                            center + half_length + half_width,
                            center - half_length + half_width])
            polygons.append(bar)
            fills.append([70, 70, 70])
        image = fill_polygons(fixed, polygons, fills)
        object_point = np.array([[obj.position[0], obj.position[1], 0.0]])  # world, on the belt
        pixel = fixed.project(object_point)[0][0]  # (u, v) of the object's center
        pixel = pixel + rng.uniform(-1, 1, 2) * cond["jitter"]  # crops are not exactly centered
        left = int(round(pixel[0] - CROP / 2))
        top = int(round(pixel[1] - CROP / 2))
        crop = image[top:top + CROP, left:left + CROP]
        crops.append(apply_conditions(crop, cond, rng))
        obj.position = obj.position + [0.06 * 0.02, 0.0]  # the belt moves 0.06 m/s for one 0.02 s frame
    label = 3 * color + shape
    return np.stack(crops), label, cond


def load(split):
    """(images (N, 48, 48, 3) uint8 RGB, labels (N,), hard (N,) bool, scene (N,)) for one split.

    The first call generates the split (a few seconds) and saves it in CACHE.
    """
    path = CACHE / f"{split}.npz"
    if path.exists():
        with np.load(path) as data:
            if tuple(data["range"]) == SPLITS[split]:  # saved from the same scene numbers
                return data["images"], data["labels"], data["hard"], data["scene"]
    images, labels, hard, scene = generate(split)
    CACHE.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, images=images, labels=labels, hard=hard, scene=scene,
                        range=np.array(SPLITS[split]))
    return images, labels, hard, scene


def generate(split):
    """Generate one split without the cache."""
    start = SPLITS[split][0]
    stop = SPLITS[split][1]
    images = []
    labels = []
    hard = []
    scene = []
    for index in range(start, stop):
        crops, label, cond = make_scene(index)
        images.append(crops)
        for frame in range(len(crops)):  # every crop of the scene shares its label and conditions
            labels.append(label)
            hard.append(cond["hard"])
            scene.append(index)
    return np.concatenate(images), np.array(labels), np.array(hard), np.array(scene)


def to_tensor(images):
    """Provided preprocessing: uint8 (N, H, W, 3) RGB -> float32 torch tensor (N, 3, H, W) in [0, 1]."""
    channels_first = images.transpose(0, 3, 1, 2)  # PyTorch puts the color channel before rows and columns
    channels_first = np.ascontiguousarray(channels_first)  # copy into that order in memory
    tensor = torch.from_numpy(channels_first)  # the same numbers, as a torch tensor
    return tensor.float() / 255.0
