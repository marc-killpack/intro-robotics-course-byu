"""Smoke-check the actual Tk window event loop on the container's display."""

from pathlib import Path
import matplotlib

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import numpy as np

from homework.models import spatial_arm
from intro_robotics.transforms import rotz
from intro_robotics.visualization import ArmPlayer, VizScene

output = Path("/workspace/tmp/foundations-gui")
output.mkdir(parents=True, exist_ok=True)
scene = VizScene()
scene.add_frame(np.eye(4), "W")
scene.add_frame(np.eye(4), "moving")
player = ArmPlayer(spatial_arm(), [0.3, -0.4, 0.5])
completed = []


def update_and_close():
    transform = np.eye(4)
    transform[:3, :3] = rotz(0.6)
    transform[:3, 3] = [0.4, 0.1, 0.2]
    scene.update(As=[np.eye(4), transform])
    scene.fit_view()
    player.sliders[1].set_val(-0.7)
    scene.fig.canvas.draw()
    player.scene.fig.canvas.draw()
    scene.fig.savefig(output / "frames.png")
    player.scene.fig.savefig(output / "spatial-arm.png")
    completed.append(True)
    plt.close("all")


timer = scene.fig.canvas.new_timer(interval=500)
timer.single_shot = True
timer.add_callback(update_and_close)
timer.start()
plt.show()
assert completed, "Tk event loop did not run the frame/slider callback"
print("TkAgg window, timer, coordinate-frame update, and spatial-arm slider verified.")
