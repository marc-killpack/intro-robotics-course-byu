"""A small geometry-based viewer; no DH tables or ROS runtime are required.

Orange dashed lines show physical joint axes. Circles mark revolute
joints; squares mark prismatic travelers. RGB lines show link frames.
This first renderer uses lines rather than detailed meshes.
"""

import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.widgets import Slider
import numpy as np

from .checks import check_scalar, check_transform, check_vector


def _set_line(line, points):
    points = np.asarray(points)
    line.set_data_3d(points[:, 0], points[:, 1], points[:, 2])


class ArmArtist:
    """Drawing objects for one arm; calculations live in the arm model."""

    def __init__(self, axes, arm, q, draw_frames):
        self.arm = arm
        self.axis_length = max(arm.reach * 0.12, 0.08)
        self.links = [
            axes.plot([], [], [], color="steelblue", linewidth=3)[0] for _ in arm.joints
        ]
        self.joints = [
            axes.plot(
                [],
                [],
                [],
                marker="o" if joint.joint_type == "r" else "s",
                color="black",
                markersize=6,
            )[0]
            for joint in arm.joints
        ]
        self.joint_axes = [
            axes.plot([], [], [], color="darkorange", linestyle="--")[0]
            for _ in arm.joints
        ]
        self.tool = axes.plot([], [], [], color="black", marker=".")[0]
        self.frame_lines = []
        if draw_frames:
            self.frame_lines = [
                [
                    axes.plot([], [], [], color=color, linewidth=1)[0]
                    for color in ("red", "green", "blue")
                ]
                for _ in range(arm.n + 2)
            ]
        self.update(q)

    def update(self, q):
        q = check_vector(q, self.arm.n, "q")
        frames = [self.arm.fk(q, i, base=True) for i in range(self.arm.n + 1)]
        joint_frames = self.arm.joint_frames(q, base=True)
        for i, (joint, frame) in enumerate(zip(self.arm.joints, joint_frames)):
            origin = frame[:3, 3]
            moving_origin = (frame @ joint.motion(q[i]))[:3, 3]
            _set_line(
                self.links[i],
                [frames[i][:3, 3], origin, moving_origin, frames[i + 1][:3, 3]],
            )
            _set_line(self.joints[i], [moving_origin])
            axis = frame[:3, :3] @ joint.axis
            _set_line(self.joint_axes[i], [origin, origin + self.axis_length * axis])
        tool_frame = self.arm.fk(q, base=True, tip=True)
        tool_position = tool_frame[:3, 3]
        _set_line(self.tool, [frames[-1][:3, 3], tool_position])
        for frame, lines in zip([*frames, tool_frame], self.frame_lines):
            origin = frame[:3, 3]
            for axis, line in enumerate(lines):
                _set_line(
                    line, [origin, origin + 0.7 * self.axis_length * frame[:3, axis]]
                )


class FrameArtist:
    """Provided RGB coordinate-frame drawing, independent of the arm class."""

    def __init__(self, axes, transform, label="", length=0.2):
        self.length = check_scalar(length, "Frame axis length")
        if self.length <= 0:
            raise ValueError("Frame axis length must be positive")
        self.lines = [
            axes.plot([], [], [], color=color, linewidth=2)[0]
            for color in ("red", "green", "blue")
        ]
        self.label = axes.text(0, 0, 0, str(label)) if label else None
        self.update(transform)

    def update(self, transform):
        self.transform = check_transform(transform, "Displayed frame")
        origin = self.transform[:3, 3]
        for i, line in enumerate(self.lines):
            _set_line(line, [origin, origin + self.length * self.transform[:3, i]])
        if self.label is not None:
            self.label.set_position_3d(origin)


class VizScene:
    """Keep add_arm/add_frame and update(qs=..., As=...) familiar."""

    def __init__(self):
        self.fig = plt.figure(figsize=(8, 6))
        self.axes = self.fig.add_subplot(projection="3d")
        self.axes.set(xlabel="x (m)", ylabel="y (m)", zlabel="z (m)")
        self.axes.set_box_aspect((1, 1, 1))
        for axis in (self.axes.xaxis, self.axes.yaxis, self.axes.zaxis):
            axis.set_major_locator(MaxNLocator(5))
        self.arms = []
        self.frames = []

    def add_frame(self, transform, label="", length=0.2):
        artist = FrameArtist(self.axes, transform, label, length)
        self.frames.append(artist)
        self.fit_view()
        return artist

    def add_arm(self, arm, q=None, draw_frames=True):
        q = np.zeros(arm.n) if q is None else q
        artist = ArmArtist(self.axes, arm, q, draw_frames)
        self.arms.append(artist)
        self.fit_view()
        return artist

    def fit_view(self):
        """Fit all displayed workspaces/frames without moving the view on updates."""
        bounds = []
        for artist in self.arms:
            arm = artist.arm
            extension = sum(
                max(abs(joint.limits)) if joint.limits is not None else 0.3
                for joint in arm.joints
                if joint.joint_type == "p"
            )
            radius = max(arm.reach + extension, 0.3)
            bounds.extend([arm.base[:3, 3] - radius, arm.base[:3, 3] + radius])
        for frame in self.frames:
            bounds.extend(
                [
                    frame.transform[:3, 3] - frame.length,
                    frame.transform[:3, 3] + frame.length,
                ]
            )
        if not bounds:
            return
        low, high = np.min(bounds, axis=0), np.max(bounds, axis=0)
        center = (low + high) / 2
        radius = max(np.max(high - low) / 2, 0.15) * 1.15
        for setter, value in zip(
            (self.axes.set_xlim, self.axes.set_ylim, self.axes.set_zlim), center
        ):
            setter(value - radius, value + radius)

    def update(self, qs=None, As=None):
        if qs is not None:
            if len(qs) != len(self.arms):
                raise ValueError("Supply one joint vector for each displayed arm")
            for artist, q in zip(self.arms, qs):
                artist.update(q)
        if As is not None:
            if len(As) != len(self.frames):
                raise ValueError("Supply one transform for each displayed frame")
            for artist, transform in zip(self.frames, As):
                artist.update(transform)
        self.fig.canvas.draw_idle()

    def show(self):
        plt.show()


class ArmPlayer:
    """One slider per Joint; the same viewer supports spatial and planar arms."""

    def __init__(self, arm, q0=None):
        q0 = np.zeros(arm.n) if q0 is None else check_vector(q0, arm.n, "q0")
        self.scene = VizScene()
        self.scene.add_arm(arm, q0)
        self.scene.fig.subplots_adjust(bottom=0.08 + 0.055 * arm.n)
        self.sliders = []
        for i, joint in enumerate(arm.joints):
            limits = joint.limits
            if limits is None:
                limits = (-np.pi, np.pi) if joint.joint_type == "r" else (-0.3, 0.3)
            if not limits[0] <= q0[i] <= limits[1]:
                raise ValueError(
                    f"Initial value for joint {i + 1} is outside its slider limits"
                )
            axes = self.scene.fig.add_axes([0.2, 0.035 + i * 0.055, 0.65, 0.025])
            unit = "rad" if joint.joint_type == "r" else "m"
            slider = Slider(
                axes, f"q{i + 1} ({unit})", limits[0], limits[1], valinit=q0[i]
            )
            slider.on_changed(self._slider_changed)
            self.sliders.append(slider)

    def _slider_changed(self, _value):
        self.scene.update([[slider.val for slider in self.sliders]])

    def show(self):
        self.scene.show()
