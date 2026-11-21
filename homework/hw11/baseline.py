"""HW11: a conventional interception controller to compare with RL.

Complete InterceptController.__call__. It receives the same observation the
learned policy receives and returns the same normalized action. Use your
HW05/HW06 code: the arm's jacob_planar and your damped_least_squares.
"""

import numpy as np

from intro_robotics import Joint, SerialArm
from intro_robotics.kinematics import damped_least_squares
from intro_robotics.rl_interception import InterceptionEnv, decode
from intro_robotics.transforms import se3


def make_arm(env):
    """A SerialArm matching the environment's planar arm (base at the origin)."""
    return SerialArm([Joint("z", tip=se3(translation=[length, 0, 0])) for length in env.lengths])


class InterceptController:
    """Feedforward the object's velocity, plus a gain times the position error."""

    def __init__(self, env, gain=4.0, damping=0.05):
        self.arm, self.n = make_arm(env), env.n
        self.gain, self.damping = gain, damping
        self.lead = 2 * env.CONTROL_PERIOD  # the command acts one period late

    def __call__(self, observation):
        s = decode(observation, self.n)  # q, dq, relative_position, relative_velocity
        # HW11: (1) J = first two rows of jacob_planar at s["q"];
        # (2) object velocity = relative velocity + tool velocity (J @ dq);
        # (3) desired tool velocity = object velocity + gain * (relative
        #     position + object velocity * self.lead);
        # (4) joint rates from damped_least_squares, divided by the speed
        #     limit and clipped to [-1, 1].
        # BEGIN SOLUTION
        jacobian = self.arm.jacob_planar(s["q"])[:2]
        object_velocity = s["relative_velocity"] + jacobian @ s["dq"]
        velocity = object_velocity + self.gain * (s["relative_position"] + object_velocity * self.lead)
        rates = damped_least_squares(jacobian, velocity, self.damping)
        return np.clip(rates / InterceptionEnv.SPEED_LIMIT, -1.0, 1.0)
        # END SOLUTION
        raise NotImplementedError("HW11: implement InterceptController.__call__")
