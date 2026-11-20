# Assignment designs following HW05

Faculty working drafts, November 17, 2026. These specify learning work,
interfaces, and evidence. HW06--HW07 have draft handouts and marked scaffolds;
HW08--HW09 have draft handouts but no student-ready scaffold. HW10 remains a
design sketch. None is in the student manifest, and all homework is unreviewed.
Schedule and project choices remain subject to instructor input.
The [unit briefs](briefs/README.md) retain the full proposed outcomes.

## HW06: configuration spaces and RRT-Connect

**Outcomes:** planning LO1--LO3 and parts of LO6--LO7. Start with a point or
circular base, then use the same planner interface for a provided two-joint
arm. Aim to implement the central two-tree algorithm with a scaffold small
enough for students who are still learning classes.

1. Sketch the workspace and a two-joint configuration space. Identify an
   obstacle collision involving a link even though the end effector is clear.
2. Trace a sample, one extension, the other tree's connect operation, and
   parent links by hand. Explain why checking only endpoints is insufficient.
3. Complete the provided extension/connection and two-tree loop, using
   supplied nearest-node, edge-validity, and path/plotting support. Keep data
   as configurations and parent indices with a small explained tree structure.
4. Run both scenes, verify start/goal and every interpolated edge, and report
   failures as well as paths over several specified random seeds.
5. Discuss a changed step size or checking resolution and compare feasibility,
   path length, and planning time using a stated budget.

**Provided:** planar robot and scene, collision and joint-limit checks,
interpolation, plotting, simple test scenarios, and RNG setup. Explain that
sampled collision checks, projected link geometry, and ordinary Euclidean
joint differences have limits. *Updated Nov 19:* HW06 now opens with a short
damped pseudo-inverse IK problem (`ik_position`) that finds two elbow
solutions for the goal; the planner still receives the supplied goal.

**Draft boundary:** `planning.py` supplies geometry; `rrt.py` contains the
two marked student methods, with input checks and a small `Tree` supplied.
A draft activity, limited public tests, private geometry/planner checks, and
a temporary stripped-copy import check exist. The current student manifest
excludes them until faculty review. Verify actual student time in a pilot.

## HW07: waypoint optimization and validation

**Outcomes:** planning LO4--LO7. A two-part homework can start with the same
HW06 obstacle and a valid seed path.

1. Given several joint waypoints, write the decision variables, fixed
   endpoints, joint bounds, collision/clearance constraints, and a sum of
   squared second differences. Explain why an untimed geometric smoothness
   cost is not physical joint acceleration.
2. Implement short path-length and smoothness functions. Use the provided
   optimizer, which calls the student's smoothness function, and vary the
   obstacle penalty rather than implementing an optimization algorithm.
3. Compare an interpolated initial guess and an RRT-generated one. Report
   solver status, path length/smoothness, time, and whether endpoints and
   interpolated edges actually pass the independent validity check.
4. Explain one failed or invalid result and decide which method or combination
   fits the scene. A finite planning/optimization failure is not proof that
   no path exists.

**Draft implementation:** a supplied NumPy optimizer compares RRT/direct
seeds for a circular base using a soft penalty, and a sampled-feasibility
optimizer refines a two-joint arm path with extra clearance. Students implement
two marked path metrics that the examples use. Both results require separate
finer edge checks. A temporary student-tree test strips HW06 and HW07 answers;
the live manifest remains HW01--HW05. SciPy SLSQP is an optional candidate,
not an installed or validated dependency. These simple waypoint solvers are
not CHOMP. RRT*, CHOMP, TrajOpt, and STOMP can be compared in lecture.

## HW08: calibration, detection, and tracking

*Revised scope, Nov 19 (TASKS.md D3):* keep the OpenCV plane map with one
held-out check, color segmentation and centroid, a new color-and-shape rule
classifier (contour vertex count), and filtered velocity from timestamps. Move
hand projection (problem 1) to HW09; cut area/bounding-box/orientation
measurements and the written truth comparison (an automatic check prints the
error).

**Outcomes:** CV1--CV5. Handwork and an image-based exercise share an oblique
fixed-camera planar scene.

1. Project one camera-frame 3D point by hand and explain depth ambiguity.
2. Estimate a plane map from four or more provided corresponding points;
   check an independent fifth point in meters. Label coordinate directions,
   the planar surface, and any undistortion assumptions.
3. Segment a contrasting object, measure its area/bounding box and a
   meaningful centroid, and identify when orientation is ambiguous.
4. Track the feature over timestamped frames, estimate planar velocity, and
   compare with separately supplied faculty truth. Report missed detections
   and one plane, image, or association limitation.

**Provided:** RGB images or documented BGR conversion, calibration points,
timestamps, and visualizations. Students use OpenCV for image work; supply
some file handling and plotting. For an extended region under perspective,
rectify before taking a metric area centroid or track a defined planar
marker. Do not treat the original-image centroid as automatically equal to a
world-plane centroid. A separate [checkerboard activity](../docs/design/checkerboard-activity.md)
now demonstrates OpenCV homographies with two synthetic views and held-out
corners. The object sequence still needs OpenCV, variation, lost-target cases,
and independent data review before becoming a student exercise.

## HW09: planar visual feedback

*Superseded Nov 19:* HW09 is being rewritten as tool-camera IBVS (TASKS.md
D5, D3): projection, then the constant-depth image Jacobian by hand; the IBVS
step on the `Controller` class with the HW05 damped solve; the lost-target
hold; stationary target only. Moving-target interception moves to project
scenario S2; the gain/delay study and fixed-camera comparison become lecture
demonstrations. The fixed-camera draft below is kept as that comparison.

**Outcomes:** VS1--VS3. Begin with a fixed camera and stationary target.

1. Form target and tool positions in a common frame, sketch an error vector,
   and predict the sign of a corrective velocity. Identify the dimensions of
   the two translational rows of `jacob_planar`.
2. Implement the short feedback calculation using a supplied damped inverse
   or bounded mapping, the robot Jacobian, and a gain. Limit commanded speeds.
3. Run the supplied simulator, plot feature/error versus time, and compare
   one change in gain, initial pose, or delay. Explain the observed behavior.
4. Stop or hold on a missing detection and demonstrate the response. Explain
   how a camera near the tool changes the image and why its pose matters.

**Provided:** arm geometry, image generation/detection interfaces, damped
inverse/limit utility, model integration, and plotting. A moving-target
exercise and an eye-in-hand control implementation depend on a tested
environment. Teams may choose either project camera. Discuss poor conditioning
and saturation practically; no full spatial Jacobian or singularity derivation
is required. Faculty NumPy pilots exercise stationary feedback and one moving
fixed-camera pickup; an OpenCV-backed, stripped student activity is pending.

## HW10: small PyTorch classifier

*Revised scope, Nov 19 (TASKS.md D3):* a short guided lab (about 3--4 hours,
two lectures). Students complete the forward/loss/backward/step lines, train
on CPU in minutes, and compare a held-out confusion matrix with their HW08 rule
classifier. The grouped-split explanation becomes a lecture question;
save/reload and the conveyor-frame trial are cut.

**Outcomes:** ML1--ML5. Use object crops from varied scenes, with geometry and
appearance designed so color alone does not reveal the shape label.

1. Identify segmentation, classification, localization, and control inputs
   and outputs. Inspect example crops, labels, and RGB/tensor shapes.
2. Explain a scene/episode-grouped train/validation/test split and why
   adjacent video frames should not be scattered across splits.
3. Trace or complete the supplied model's prediction, loss, gradient, and
   optimizer update. Train on a measured CPU budget; save and reload it.
4. Report held-out accuracy and class-wise errors or a confusion matrix,
   inspect failures, and compare a supplied geometry/color rule on the same
   eligible crops. Try the model on a prepared conveyor frame.

**Provided:** labeled dataset and grouped split IDs, preprocessing, a short
model and training scaffold, plotting, a rule baseline, and a checkpoint.
Use the same preprocessing and class mapping at inference. The chosen PyTorch
and dependency versions, independent data, and CPU runtime are not tested
yet. A project team may use either a learned or rule-based classifier.

## RL introduction and reward-shaping homework

*Revised Nov 19 (TASKS.md D3):* two lectures after the project launch (rollouts
in simulation, reward, the policy as a network, PPO intuition, SB3). The short
homework changes only the reward for a supplied task and compares variants;
teams may use RL late in the project to improve score and speed. The task
(state-based interception, with planar reaching as the fallback) is in
TASKS.md D3. The earlier lab design below is kept for reference.

### Earlier design: week-11 guided RL lab

**Outcomes:** RL1--RL5. Use a prepared planar reaching example if it works
reliably; otherwise use a small provided control environment and explain the
robot analogy. Students identify observations, actions, reward, termination,
and policy; run or inspect a checkpoint; and compare success/failures over
independent cases with an available baseline. Discuss training budget and
seed variability. A short in-class activity or reflection is the default,
not a second full homework during the project transition.

Provide an environment, evaluated checkpoint, script/plots, and fallback
recording. Students do not implement PPO or a custom Gymnasium wrapper.
Learning from visual-servo demonstrations and further RL training are
optional project extensions only. PPO requires new interaction; a plain
cloning model is not automatically a compatible SB3 policy.

## Common review before student release

- Check the problem count and overlapping deadlines with a student pilot.
- Approve assigned versus provided functions and create a separately stripped
  student copy. Do not include faculty pilots or ground truth inadvertently.
- Provide unit/frame conventions, limited public checks, instructor checks,
  data provenance, expected run commands, and a usable fallback.
- Keep CPU-only operation and offline work after setup as goals to verify on
  representative Windows/AMD64 and Apple Silicon/ARM64 environments.
