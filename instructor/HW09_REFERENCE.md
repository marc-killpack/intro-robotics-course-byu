# HW09 faculty reference: planar visual feedback

Draft reference; the assignment and its intended student support are not yet
reviewed or released.

1. `e = (0.05, 0.03)` m and `v_d = (0.075, 0.045)` m/s. With the supplied
   diagonal `J_p`, the exact unbounded rates are `(0.75, 0.225)` rad/s.
   Componentwise limits give `(0.60, 0.225)` rad/s and the resulting tool
   velocity is `(0.060, 0.045)` m/s. The first two Jacobian rows map joint
   rates to XY velocity; the third row is not used for this position task.
2. Form target minus tool in one frame, use the first two rows of the
   completed `jacob_planar`, call the supplied damped solve and limit helpers,
   and return a zero vector if the target is missing. The detector, not true
   simulator object position, supplies the target measurement to the controller.
3. Compare gains from identical initial conditions. A zero velocity *request*
   on target loss does not instantly stop an acceleration-limited arm. Results
   depend on the future student-ready detector, simulator, gain, and limits;
   do not set a grading threshold from the faculty prototype.
4. A camera fixed to the moving tool has a changing pose, so its plane
   homography changes. An offset means that image center and the tool's desired
   grasp location generally differ; the camera-to-tool transform or a suitable
   reference observation is needed.

The student controller scaffold, image interface, and reproducible scenarios
still need to be built and reviewed. No spatial Jacobian or singularity theory
is required for this draft.
