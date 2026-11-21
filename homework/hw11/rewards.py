"""HW11: three reward functions for the interception task.

Each function receives the info dictionary the environment returns every
step and returns one number. Useful entries:

    info["distance"]        tool-to-object distance, meters
    info["relative_speed"]  |v_object - v_tool|, m/s
    info["success"]         True on the step the pickup condition is met
                            (the episode then ends)
    info["action"]          the normalized joint command just chosen, in [-1, 1]

The environment ends an episode on success or after 4 s. The training
script calls one of these by name: --reward sparse, distance, or shaped.
"""

import numpy as np

SUCCESS_BONUS = 10.0


def sparse_reward(info):
    """1 on success, otherwise 0. Nothing tells the policy it is getting closer."""
    # HW11: one line.
    # BEGIN SOLUTION
    return 1.0 if info["success"] else 0.0
    # END SOLUTION
    raise NotImplementedError("HW11: implement sparse_reward")


def distance_reward(info):
    """Minus the distance every step, plus SUCCESS_BONUS on success."""
    # HW11: closer is better, so the per-step reward rises toward zero.
    # BEGIN SOLUTION
    return -info["distance"] + (SUCCESS_BONUS if info["success"] else 0.0)
    # END SOLUTION
    raise NotImplementedError("HW11: implement distance_reward")


def shaped_reward(info, speed_weight=0.5, action_weight=0.01):
    """distance_reward, minus speed_weight * relative speed, minus
    action_weight * |action|^2 (a small price for large commands)."""
    # HW11: add the velocity-matching and action terms to distance_reward.
    # BEGIN SOLUTION
    action = np.asarray(info["action"], float)
    return (distance_reward(info) - speed_weight * info["relative_speed"]
            - action_weight * float(action @ action))
    # END SOLUTION
    raise NotImplementedError("HW11: implement shaped_reward")


REWARDS = {"sparse": sparse_reward, "distance": distance_reward, "shaped": shaped_reward}
