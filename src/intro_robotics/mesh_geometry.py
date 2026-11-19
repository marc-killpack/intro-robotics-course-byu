"""Geometry helpers for drawing an explicit-joint arm as solid 3D meshes."""

import numpy as np

from .checks import check_vector


def arm_geometry(arm, q):
    """Return world-space link points and physical joint axes for one pose.

    The arm's own FK remains the source of the frames, so a student must
    complete the assigned FK method before the viewer can draw the arm.
    """
    q = check_vector(q, arm.n, "q")
    frames = [arm.fk(q, i, base=True) for i in range(arm.n + 1)]
    joint_frames = arm.joint_frames(q, base=True)
    joints = []
    for i, (joint, frame) in enumerate(zip(arm.joints, joint_frames)):
        moving_frame = frame @ joint.motion(q[i])
        joints.append(
            {
                "start": frames[i][:3, 3].copy(),
                "origin": frame[:3, 3].copy(),
                "position": moving_frame[:3, 3].copy(),
                "end": frames[i + 1][:3, 3].copy(),
                "axis": frame[:3, :3] @ joint.axis,
                "joint_type": joint.joint_type,
            }
        )
    tool = arm.fk(q, base=True, tip=True)
    return joints, frames, tool


def cylinder_mesh(start, end, radius, sides=16):
    """Return vertices and triangular faces for a capped cylinder between points."""
    start, end = np.asarray(start, dtype=float), np.asarray(end, dtype=float)
    direction = end - start
    length = np.linalg.norm(direction)
    if length < 1e-12:
        return np.empty((0, 3)), np.empty((0, 3), dtype=int)
    axis = direction / length
    reference = np.eye(3)[np.argmin(np.abs(axis))]
    first = np.cross(axis, reference)
    first /= np.linalg.norm(first)
    second = np.cross(axis, first)
    angle = np.arange(sides) * (2 * np.pi / sides)
    ring = radius * (
        np.cos(angle)[:, None] * first + np.sin(angle)[:, None] * second
    )
    vertices = np.vstack((start + ring, end + ring, start, end))
    faces = []
    for i in range(sides):
        j = (i + 1) % sides
        faces.extend(
            (
                [i, j, i + sides],
                [j, j + sides, i + sides],
                [2 * sides, j, i],
                [2 * sides + 1, i + sides, j + sides],
            )
        )
    return vertices, np.asarray(faces, dtype=int)


def combine_meshes(parts):
    """Combine (vertices, faces, RGBA color) parts into one drawable mesh."""
    vertices, faces, colors = [], [], []
    offset = 0
    for points, triangles, color in parts:
        if not len(points):
            continue
        vertices.append(points)
        faces.append(triangles + offset)
        colors.append(np.tile(color, (len(triangles), 1)))
        offset += len(points)
    if not vertices:
        return np.empty((0, 3)), np.empty((0, 3), dtype=int), np.empty((0, 4))
    return np.vstack(vertices), np.vstack(faces), np.vstack(colors)
