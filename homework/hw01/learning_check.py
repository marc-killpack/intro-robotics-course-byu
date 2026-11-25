"""Check PyTorch, Gymnasium, and Stable-Baselines3 (used in HW10 and HW11).

Run in a container shell, from /workspace, with the browser desktop open:

    python homework/hw01/learning_check.py

The script trains a small neural network with reinforcement learning to
balance a pole on a moving cart (Gymnasium's CartPole task). Every few
seconds it tests the network and prints how long the pole stayed up. At the
end a window shows the untrained and trained networks side by side.

Nothing here is homework; you do not need to change this file.
"""

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Rectangle
import numpy as np
import gymnasium as gym
import stable_baselines3 as sb3
from stable_baselines3 import PPO
import torch

MAX_STEPS = 500  # CartPole stops an episode after 500 steps (10 seconds)
ROUNDS = 8  # training rounds; each takes a few seconds
STEPS_PER_ROUND = 2048  # simulation steps the network practices per round


def run_episode(model, explore):
    """Let the network control the cart once.

    Returns the states to draw and the number of steps the network lasted.
    An episode fails when the pole tilts more than 12 degrees or the cart
    leaves the track; after a failure the pole keeps falling, only so the
    picture shows it.

    With explore=True the network picks actions at random in proportion to
    its preferences, as it does while practicing; an untrained network has
    no preference yet, so it pushes the cart left or right at random.
    """
    env = gym.make("CartPole-v1")
    state, info = env.reset(seed=1)
    states = [state]
    for step in range(MAX_STEPS):
        action, _ = model.predict(state, deterministic=not explore)
        state, reward, failed, out_of_time, info = env.step(action)
        states.append(state)
        if failed or out_of_time:
            break
    env.close()
    steps = len(states) - 1
    if failed:
        x, angle, rate = state[0], state[2], state[3]
        for frame in range(100):  # a falling stick: angle'' = 14.7 sin(angle)
            rate = rate + 0.02 * 14.7 * np.sin(angle)
            angle = np.clip(angle + 0.02 * rate, -np.pi / 2, np.pi / 2)
            states.append([x, 0.0, angle, rate])
    return np.array(states), steps


def draw_cart(ax, title):
    """Set up one panel; return the cart, pole, and text it will update."""
    ax.set_xlim(-2.4, 2.4)
    ax.set_ylim(-0.3, 1.3)
    ax.set_aspect("equal")
    ax.set_yticks([])
    ax.set_xlabel("cart position (m)")
    ax.set_title(title)
    ax.axhline(0, color="gray")
    cart = Rectangle((-0.25, -0.1), 0.5, 0.2, color="tab:blue")
    ax.add_patch(cart)
    (pole,) = ax.plot([], [], color="tab:orange", linewidth=6)
    label = ax.text(-2.3, 1.1, "")
    return cart, pole, label


def show(before, after):
    """Animate both episodes side by side, in real time (50 steps per second)."""
    fig, axes = plt.subplots(1, 2, figsize=(10, 2.8))
    fig.canvas.manager.set_window_title("Learning check")
    panels = [
        (before, draw_cart(axes[0], "Before training")),
        (after, draw_cart(axes[1], "After training")),
    ]

    def update(frame):
        for (states, steps), (cart, pole, label) in panels:
            k = min(frame, len(states) - 1)  # a finished episode holds its last pose
            x, angle = states[k, 0], states[k, 2]  # angle is 0 when upright
            cart.set_x(x - 0.25)
            pole.set_data([x, x + np.sin(angle)], [0, np.cos(angle)])
            if k < steps:
                label.set_text(f"step {k}")
            elif steps < MAX_STEPS:
                label.set_text(f"failed after {steps} steps")
            else:
                label.set_text(f"balanced all {steps} steps")
        return []

    frames = max(len(before[0]), len(after[0])) + 50  # hold the end for one second
    animation = FuncAnimation(fig, update, frames=frames, interval=20, repeat=True)
    fig.tight_layout()
    plt.show()
    return animation


model = PPO("MlpPolicy", "CartPole-v1", seed=1)
before = run_episode(model, explore=True)
print(f"Untrained network: failed after {before[1]} steps.")
print("Training (under a minute)...")
for round_number in range(1, ROUNDS + 1):
    model.learn(STEPS_PER_ROUND, reset_num_timesteps=False)
    after = run_episode(model, explore=False)
    print(f"  after {round_number * STEPS_PER_ROUND:5d} practice steps: "
          f"balanced {after[1]} of {MAX_STEPS} steps")

print(f"torch {torch.__version__}, Gymnasium {gym.__version__}, "
      f"SB3 {sb3.__version__}: OK")
print("Close the window to finish.")
show(before, after)
