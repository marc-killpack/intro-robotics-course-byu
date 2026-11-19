"""Manual graphical checks of the adapted scene and its slider player."""

import argparse
from pathlib import Path

import cv2  # Check the OpenCV-first import order on Linux and Windows.
import numpy as np

from homework.models import planar_arm, spatial_arm
from intro_robotics.adapters import from_dh
from intro_robotics.visualization_3d import ArmPlayer, QTimer, VizScene


def save_image(widget, path):
    assert widget.grabFramebuffer().save(str(path))
    image = cv2.imread(str(path))
    assert image is not None and np.count_nonzero(np.any(image < 180, axis=2)) > 2000


def run_player(destination, planar):
    arm = planar_arm() if planar else spatial_arm()
    player = ArmPlayer(arm, q=[0.6, -0.5, 0.4], autoplay=False)
    player.window.show()
    result = {"error": None}

    def check():
        try:
            for slider, degrees in zip(player.sliders, [60, -30, 45]):
                slider.setValue(degrees * 2)  # The original player uses half-degrees.
            np.testing.assert_allclose(player.q, np.deg2rad([60, -30, 45]))
            player.velocity_checkbox.setChecked(True)
            if planar:
                assert player.velocity_checkbox.isChecked()
                rates = np.array([0.2, -0.1, 0.3])
                player.set_state(qd=rates)
                for box in player.linear_checkboxes + player.angular_checkboxes:
                    box.setChecked(True)
                velocity = arm.jacob_planar(player.q, base=True, tip=True) @ rates
                np.testing.assert_allclose(player.velocity_overlay.linear_total[:2], velocity[:2])
                np.testing.assert_allclose(player.velocity_overlay.angular_total[2], velocity[2])
            else:
                assert not player.velocity_checkbox.isChecked()
                assert "planar" in player.velocity_status.text().lower()
            player.app.processEvents()
            name = "planar-player" if planar else "spatial-player"
            save_image(player.viz_widget, destination / f"{name}-view.png")
            assert player.window.grab().save(str(destination / f"{name}-window.png"))
            print(name, "slider values", player.q, "OpenCV", cv2.__version__)
        except Exception as error:
            result["error"] = error
        finally:
            player.window.close()
            player.app.quit()

    QTimer.singleShot(1200, check)
    player.app.exec()
    if result["error"] is not None:
        raise result["error"]


def run_scene(destination):
    scene = VizScene()
    result = {"error": None}

    def check():
        try:
            arm = spatial_arm()
            first = scene.add_arm(arm, draw_frames=True, label_axes=True,
                                  q=[0.3, -0.4, 0.2])
            dh_arm = from_dh([[0, 0, 0.25, 0], [0, 0, 0.2, 0]])
            second = scene.add_arm(dh_arm, [0.1, 0.3])
            np.testing.assert_allclose(second.q, [0.1, 0.3])
            scene.add_frame(np.eye(4), label="world", axes_label="W")
            scene.add_marker([0.2, 0.1, 0.1], radius=0.04)
            scene.add_obstacle([0.4, 0.2, 0.1], rad=0.06)
            arrow = scene.add_arrow([0.1, 0.2, 0.1], pos=[0.1, 0.1, 0.1])
            circular = scene.add_circular_arrow([0, 0, 0.4], pos=[0.1, 0.1, 0.1])
            scene.update(qs=[[0.4, -0.3, 0.5], [0.2, -0.1]],
                         As=[np.eye(4)], poss=[[0.25, 0.1, 0.1]])
            np.testing.assert_allclose(first.q, [0.4, -0.3, 0.5])
            arrow.update(vector=[0.2, 0.1, 0])
            circular.update(vector=[0, 0, 0.2])
            scene.app.processEvents()
            save_image(scene.window, destination / "adapted-vizscene.png")
            old_center = scene.window.opts["center"]
            far_frame = np.eye(4)
            far_frame[:3, 3] = [3, -1, 0.5]
            scene.update(As=[far_frame])
            assert scene.window.opts["center"] == old_center
            scene.fit_view()
            assert scene.window.opts["center"].x() > 0.8
            scene.remove_arm(1)
            assert len(scene.arms) == 1
            scene.remove_marker()
            scene.remove_arrow()
            scene.remove_circular_arrow()
            scene.remove_obstacle()
            scene.remove_frame()
            print("Original scene: frames, markers, arrows, obstacles, two arms, DH and removal passed.")
        except Exception as error:
            result["error"] = error
        finally:
            scene.close_viz()
            scene.app.quit()

    QTimer.singleShot(500, check)
    scene.app.exec()
    if result["error"] is not None:
        raise result["error"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--mode", choices=["spatial", "planar", "scene"], default="spatial")
    args = parser.parse_args()
    args.destination.mkdir(parents=True, exist_ok=True)
    if args.mode == "scene":
        run_scene(args.destination)
    else:
        run_player(args.destination, args.mode == "planar")
