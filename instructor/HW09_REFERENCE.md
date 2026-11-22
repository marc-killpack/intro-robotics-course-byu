# HW09 faculty reference: tool-camera visual servoing

Draft key, rewritten November 19 for tool-camera IBVS (TASKS.md D3, D5).
Keep outside student copies. The canonical code answers are the two marked
regions of `homework/hw09/ibvs_controller.py`; numbers below were computed
with them. The earlier fixed-camera draft is now a lecture comparison
(`examples/ibvs_lecture_demos.py`).

1. (a) `u = 180(0.11)/0.30 + 160 = 226`, `v = 180(-0.025)/0.30 + 120 = 105`.
   (b) Doubling every coordinate leaves `x/z` and `y/z` unchanged: a pixel
   fixes a ray, not a point. Here every object lies on the belt plane, the
   arm is planar, and the actuator is up, so the depth is known:
   `Z = 0.25 + 0.05 = 0.30` m. (c) The point below the tool is `+0.06` m
   along camera x from the camera and `0.30` m below it:
   `s* = (180(0.06)/0.30 + 160, 120) = (196, 120)`. It differs from the center
   because the camera is offset from the tool; centering the object would put
   it under the camera, 6 cm from the tool.
2. (a) A belt point fixed in the world has camera coordinates changing at
   `-v_c` (and constant `z_c = Z`), so `u_dot = f x_dot/Z = -(f/Z) v_x`,
   likewise for v. (b) `e_dot = s_dot = -(f/Z) v_c`; choose
   `v_c = lambda (Z/f) e`. lambda is 1/s; Z/f is m/pixel (1/600 here).
   (c) Camera x = tool x = `(cos psi, sin psi)`; camera y = -tool y =
   `(sin psi, -cos psi)`; the columns of the matrix are those axes.
   (d) `e = (30, -15)` px, `v_c = (0.10, -0.05)` m/s, and with
   `psi = pi/2`, `v_w = (-0.05, 0.10)` m/s. The object is at camera
   `(0.11, -0.025)`, tool frame `(0.11 - 0.06, 0.025) = (0.05, 0.025)`, world
   offset `R_z(pi/2)(0.05, 0.025) = (-0.025, 0.05)` m; times lambda = 2 it
   equals `v_w`. With constant depth and no camera rotation, IBVS commands the
   same velocity as position feedback would, without knowing either position.
3. (a) `ibvs_velocity` is six lines (error, `gain*depth/focal*error`, cos
   and sin, the 2-by-2 rotation). (b) `joint_rates`: zero vector on `None`; otherwise limit
   the speed and call `damped_least_squares(jacobian, [vx, vy, 0], damping)`.
   The heading is held because problem 2 assumed a camera that does not
   rotate; a rotating camera turns the image about the optical axis and adds
   image motion the law does not model. Four joints minus three task rows
   leave one redundant joint. Accept the two-row solve plus a reason the
   heading drift is small, if argued.
4. (a) Seed 1: error 46.2 px at the start, 3.6 px when the pick was
   requested at 1.76 s, pickup succeeded. Seed 2: 32.9 px to 3.5 px, pick at
   1.52 s, succeeded. After the blackout the error took 0.58 s (seed 1, from
   26.4 px at 0.70 s) and 0.52 s (seed 2) to fall by a factor of e, against
   `1/lambda = 0.5` s; without the blackout, 0.60 s from the start. Reasons:
   the acceleration limit at the start and after the blackout, the one-period
   delay, and damping (the damped solve delivers slightly less than the
   requested velocity). (b) All 20 blank-period commands are exactly zero. The
   arm keeps moving briefly because the zero request takes effect one period
   later and the acceleration limit then brings it to rest gradually. A stale
   measurement of a moving object points at where it was, so the arm would
   chase an old position (and, with the gain, keep accelerating toward it).
   (c) From a model: f, Z, s* (camera mount), psi (heading from FK), and the
   Jacobian. From the image: only s. A base translation changes neither psi nor
   the planar Jacobian, and the loop stops when the image error is zero, so
   the error never enters. Measure-then-move trusts the modeled tool position
   and stops 3 cm from the object (pick radius 2.5 cm). Lecture demonstration
   results: 3/3 picks for both at 0 and 1 cm base error; at 3 cm,
   measure-then-move 0/3 and IBVS 3/3. (d) `||e|| = v f/(lambda Z) =
   0.06(180)/(2(0.30)) = 18` px, which is `v/lambda = 0.03` m, more than the
   2.5 cm pick radius. Add the object's velocity as feedforward (estimated from
   the fixed camera's track): `v_w = v_object + R v_c`.

Gain study (lecture demonstration, `examples/ibvs_lecture_demos.py`, seed 1,
speed limit raised to 1 m/s): gain 2 picks at 1.36 s; gain 8 at 0.72 s; gain
20 overshoots and rings but picks at 1.34 s; gain 40 oscillates with growing
amplitude, loses the object, and never picks. The one-period delay and the
acceleration limit set the usable gain.

Review notes: workload target is one week (two problems by hand, about 15
lines of code, short runs). The supplied detector is a color threshold;
HW08 teaches detection. No spatial Jacobian, camera rotation term, or
singularity theory is required.
