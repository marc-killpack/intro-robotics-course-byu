# Draft lecture outlines from IK through the project launch

Faculty working draft, November 17, 2026; reworked November 20 for the
D3/D5 decisions (one IK session; three vision, three servoing, two
supervised-learning, two project-launch, and two RL sessions). Each row
totals 50 minutes and adds a specific activity or checkpoint. Session IDs
give the slot in the [42-session calendar](semester-integration.md) as
week.meeting. These are lecture outlines, not completed slides or measured
class timings.

## Inverse velocity and IK (week 6)

| Session | 50-minute sequence | Active check / preparation |
| --- | --- | --- |
| IK1 (6.1): From tool goals to joint motion | 10 min square case: solve $J_{xy}\dot q=v$, and the direction lost where $\det J_{xy}=0$ (HW06 problem 1(a)); 15 min redundant arm: the minimum-norm solve $J^T(JJ^T)^{-1}v$, the null space, and damping as a tradeoff near a straight arm (HW06 1(c--d)); 15 min IK by iteration: treat the XY error as a velocity, step with `damped_least_squares`, clip to joint limits, stop at a tolerance (HW06 `ik_position`); 10 min worked example: HW06's target from two starting guesses gives the two elbow solutions | Why can the error be treated like a velocity, and why does the step size matter? Students predict which elbow solution each start reaches. This is the damped pseudo-inverse IK the planning, servoing, and project units reuse (D5(f)). |

## Planning: six proposed lectures

| Session | 50-minute sequence | Active check / preparation |
| --- | --- | --- |
| P1: Configurations and collisions | 10 min point/circular base; 15 min two-joint arm configuration space; 15 min state versus edge validity; 10 min worked example | Use the HW06 activity (faculty master). Students identify why two valid endpoints can still have a colliding connection. |
| P2: RRT-Connect | 5 min one-tree growth; 15 min two trees and connection; 20 min trace a sample and several extensions; 10 min step size, budget, and failure | Hand out a tiny tree with parent indices; students reconstruct the path and check an edge. |
| P3: Transfer to an arm and RRT* | 15 min joint-space scene; 10 min inspect a success and a failed trial; 5 min RRT* parent/rewiring idea; 20 min from a geometric path to timed motion: waypoint times, `trajectory_msgs/JointTrajectory`, cubic Hermite interpolation between waypoints, and a subscriber node that publishes `JointState` at 50 Hz (HW07 problem 5) | Compare the arm and configuration-space panels. Mark one colliding arm pose on the plot. RRT* is a conceptual comparison. |
| P4: Optimization formulation | 25 min variables, costs, constraints, initial guesses, and local minima; 15 min waypoint formulation; 10 min obstacle-avoidance difficulty | Label the intermediate joint configurations, fixed endpoints, smoothness cost, and collision requirements. |
| P5: Refining a route | 10 min waypoint cost and validity; 15 min CHOMP idea; 10 min provided solver demonstration; 10 min compare initial paths and local methods; 5 min validate output | Ask whether a lower objective proves collision freedom. Show the separate edge check; the simple solver is not CHOMP. |
| P6: Cartesian tasks and position-only optimization | 10 min joint goal versus desired tool path; 20 min working planar example: optimize joint waypoints so the tool hits Cartesian positions, orientation free (D9); 10 min the assigned simplified planar reading of the Bodily, Allen, and Killpack paper; 5 min hard/soft task requirements; 5 min choose a method | Classify a painting waypoint as a hard requirement or a soft cost. Students have implemented damped pseudo-inverse IK (IK1); use it for the painting task. Demo: `python -m examples.position_only_branching --show` (then `--kappa 0` and `--no-obstacle`); reading: [docs/readings/position_only_branching.tex](../readings/position_only_branching.tex). |

All six planning sessions are currently reserved. Keep the shorter combined
outline as a contingency only if the actual holiday/exam calendar removes time.
The P5 base and arm demonstration is the HW07 activity run with the completed
faculty master: `python -m homework.hw07.hw07_optimization --show`. P1--P3 can
use the HW06 activity the same way.

## Computer vision (weeks 8--9)

| Session | 50-minute sequence | Active check / preparation |
| --- | --- | --- |
| V1 (8.2): Camera geometry | 10 min pixels and frames ($u$ right, $v$ down; pixel centers at $u+0.5$); 15 min pinhole projection and depth ambiguity; 15 min intrinsics and pose (the simulated cameras have no lens distortion); 10 min a plane-to-image map as a homography: why it has 8 unknowns and needs the divide by the third coordinate | Project one camera-frame point by hand and explain why one pixel alone does not determine depth (prepares HW09 problem 1). |
| V2 (8.3): Homography, segmentation, and shape rules | 15 min fit and check a plane map: the two-view checkerboard demo (`python -m examples.checkerboard_homography`, automatic corner detection), 4 corners fit and 31 checked, one view's map on the other view (HW08 problem 1); 10 min what a feature is (`python -m examples.feature_demo`): Harris and Shi-Tomasi fire on all 75 board corners and about 50 other points, so a board detector needs the grid's structure (`findChessboardCorners`); SIFT and ORB keypoints carry descriptors, but on the repeated checkerboard RANSAC accepts a homography wrong by about 95 px, while two views of a belt with about five distinct objects match within 1 px (SURF needs a non-free OpenCV build; ORB is the free alternative); 5 min the project camera's marks and the above-plane error; 10 min color masks (`cv2.inRange`, tolerance), outer contours, and the corner-count shape rule (`cv2.approxPolyDP`); 10 min cut-off objects and the rule table (`task.rules`) | Why does the error on the fit corners say nothing about the map? Predict where a plane map puts a point held above the belt. |
| V3 (9.1): Tracking, velocity, and filtering | 10 min association: predict each track, gate, and match by color and shape; 10 min timestamps and missed frames; 15 min two-point difference versus a least-squares line: the belt moves 1.2 mm per frame, about the position error, so the difference is off by about 30 mm/s and the fit by about 0.5 mm/s; 10 min window length versus lag; 5 min run `python -m homework.hw08.hw08_perception --realism on --drop 0.3` | Compare a two-point difference with a least-squares fit on uneven timestamps (HW08 problem 3(a)); distinguish a missing detection from a measurement at the origin. |

Prepared (Nov 20): the HW08 checkerboard and moving-belt activities run the
completed faculty functions in `src/intro_robotics/vision.py`; both support
`--save` for slides. The project's checkerboard calibration (PL1) reuses
V1--V2 with automatic corner detection.

## Visual servoing (weeks 9--10)

| Session | 50-minute sequence | Active check / preparation |
| --- | --- | --- |
| VS1 (9.2): Measure-then-move versus image-based | 10 min measure-then-move: fixed-camera map plus IK on the measured target (position-based servoing is "IK with a measured goal"); 10 min what that relies on: the calibration, the base pose, and the link lengths; 15 min demonstration: arm base modeled 0, 1, and 3 cm off; measure-then-move picks 3/3, 3/3, and 0/3, IBVS 3/3 each time; 15 min the tool camera: offset from the tool, the known belt depth $Z=0.30$ m, and the desired pixel $s^*$ below the tool (not the image center) | Project a camera-frame point by hand and find $s^*$ (HW09 problem 1). Demo: `python examples/ibvs_lecture_demos.py --save tmp/ibvs_demos.png` (the model-error panel). |
| VS2 (9.3): The planar image Jacobian | 15 min derive $\dot u=-(f/Z)v_x$ and $\dot v=-(f/Z)v_y$ for a camera translating parallel to the belt, so $\dot s=-(f/Z)v_c$; 10 min choose $v_c=\lambda(Z/f)e$ so $\dot e=-\lambda e$; units of $\lambda$ and $Z/f$; 10 min camera axes in the world with the tool heading $\psi$; 15 min worked example: $s=(226,105)$, $\lambda=2$ s$^{-1}$, $\psi=\pi/2$ gives $v_w=\lambda(p_{\rm object}-p_{\rm tool})$ without computing either position | Students compute $e$, $v_c$, and $v_w$ for the worked example before it is shown (HW09 problem 2(d)). |
| VS3 (10.1): Image-based servoing: integration and limits | 10 min joint rates from the HW06 damped solve with all three rows of `jacob_planar` and zero heading rate (why hold the heading; how many joints are left over); 10 min speed limit; 15 min demonstration: gains 2, 8, 20, and 40 with the one-period delay (picks at 1.36, 0.72, and 1.34 s; gain 20 rings; gain 40 diverges); 5 min a lost target: send zero joint rates (HW09's camera blackout); 10 min a moving object: the lag where $\lambda(Z/f)$ times the pixel error equals the object's speed, and the feedforward term that removes it (project S2) | For $\lambda=2$ s$^{-1}$, $f=180$ px, $Z=0.30$ m, and 0.06 m/s, estimate the lag: about 18 px or 3 cm (HW09 problem 4(d)). Demo: the gain panel of `ibvs_lecture_demos.py`; the student activity is `python -m homework.hw09.hw09_ibvs`. |

Prepared (Nov 19): HW09 runs on the project's `Controller` class and
lockstep runner, so these sessions use the project's arm, cameras, limits,
and one-period delay. The demonstrations use the faculty answer keys and run
from the faculty tree. A full spatial image Jacobian is outside this
course's scope.

## Supervised learning and PyTorch (week 10)

| Session | 50-minute sequence | Active check / preparation |
| --- | --- | --- |
| L1 (10.2): Supervised perception and the training loop | 10 min where a learned label fits the conveyor pipeline, and when the HW08 rules stop working (noise, blur, partly visible objects, lighting changes); 10 min crops, labels, and scene-grouped splits; 15 min tensors, the small supplied model, scores, and the loss; 15 min one training update: zero the gradients, forward, backward, optimizer step (the lines HW10 leaves to students) | Label the image and output shapes for one batch; decide whether adjacent frames from one scene belong in different splits, and explain why. |
| L2 (10.3): Train and evaluate on harder images | 10 min train on the CPU (or load the prepared checkpoint); 15 min held-out confusion matrices for the network and the HW08 rule classifier on clean and on harder images; 15 min inspect mistaken crops: segmentation, classification, or both; 10 min using a label in the project, and when the rules are enough | Predict which confusions the rule classifier makes on blurred or partly visible objects before showing the matrix. |

HW10 (being built Nov 20) is the short guided lab behind L1--L2: students
complete the training loop, train a small model on the CPU, and compare
confusion matrices with their HW08 rule classifier. Its harder images
(noise, blur, partial views, lighting) are where the rules degrade and the
learned classifier earns its place; on clean simulator images the rules are
already 100% correct. Use a prepared checkpoint if live training is slow.

## Project launch (week 11)

| Session | 50-minute sequence | Active check / preparation |
| --- | --- | --- |
| PL1 (11.1): Architecture, scenarios, runner, and calibration | 10 min the task and score (+10 sorted, -5 dropped or wrong bin; time counts through throughput); 10 min the `Controller` contract: `Observation`, `Task`, `Command`, the one-period delay, and object truth never given; 5 min scenarios S1--S3, the realism switch, and the moved camera in S3 and the graded run; 5 min the lockstep runner (`python -m homework.project.run`, graded) versus live ROS (watching and the demonstration); 20 min calibration in class: `task.calibration_image` and the fixed board orientation, write `find_board_corners` (detect, refine, add 0.5, reverse if needed), run `check_calibration` | Start `find_board_corners` in class; checkoff 1 is at the start of PL2, one lecture day later (lecture-before-due rule). Ask why the graded camera moves and why `--warp` is a fair test of that. |
| PL2 (11.2): Integration: ROS plumbing and RViz debugging | 5 min checkoff 1: `python -m homework.project.check_calibration --scenario s1` and `--scenario s3 --warp 5` report OK; 10 min the live graph: simulator, cameras, the wrapper around the student's class, `robot_state_publisher`; 10 min inspect it: `ros2 node info`, `ros2 topic hz` on the camera images, `ros2 interface show conveyor_interfaces/msg/PickupRequest`; 10 min falling behind at 50 Hz (`rate:=0.5`) and why graded scores come from `run.py`; 15 min plan the controller: a state machine (find, approach, pick, carry, release) built from HW05, HW08, and HW09, and the week-12 S1 checkoff | Each team sketches its state machine and names which homework function each state calls. Prepare: `ros2 launch homework/project/project.launch.py scenario:=s2` with the reference controller for a demonstration. |

The checkoff table is in the [student guide](../../homework/project/README.md#checkoffs-draft):
calibration at PL1, S1 in week 12, S2 with realism in week 13, and the
graded evaluation in week 14.

## Reinforcement learning (weeks 11--12)

| Session | 50-minute sequence | Active check / preparation |
| --- | --- | --- |
| RL1 (11.3): RL as feedback | 10 min the control goal and a rollout; 15 min observation, action, reward, return, and episodes; terminated versus truncated; 10 min the HW11 interception task: 50 Hz, limits, one-period delay, success as 2.5 cm and 5 cm/s for three periods; 10 min sparse, distance, and shaped rewards for one step by hand; 5 min reward versus the success condition | Compute the three rewards for one step (HW11 problem 1); identify the measured observations and the bounded actions. |
| RL2 (12.1): The policy as a network, PPO intuition, and SB3 | 5 min at the start: launch two full training runs side by side, the same task with two different rewards (`python -m homework.hw11.train --reward distance --out tmp/lecture/distance.zip` and `--reward sparse`), and ask students to predict which will learn; 10 min trace observation to action through the policy network; 10 min PPO intuition: collect rollouts, improve the policy a little at a time (no derivation); 10 min "RL relearns IK": the prepared reaching policy beside the damped-least-squares baseline on the same held-out cases; 10 min the runs have finished (about 7 min side by side on the faculty laptop): evaluate both on the held-out cases (Nov 20: distance 100/100, sparse 4/100); 5 min reading results: success, time, and failures together, seeds, and why sparse reward rarely finds the goal (homework results: distance 99--100%, shaped 98--99%, sparse about 0%, baseline 100%) | Explain what the network represents and why the baseline needed a model but the policy needed many rollouts. Commands are in the [HW11 faculty README](../homework/hw11/README.md); checkpoints protect the lecture if live training is slow. |

HW11 (reward shaping, week 12) follows RL2. Teams may use RL late in the
project to improve score or speed; imitation and RL improvements are
optional project extensions.

## Project weeks 12--14

Eight project sessions follow RL2 (12.2 through 14.3): one or two extension
lectures a week, one help session a week, and project work. Checkoffs are S1
(week 12), S2 with realism on (week 13), and the graded evaluation in week
14 (S3 structure, new seeds, a new rule table, and a moved camera), with
demonstrations in the last help session. Optional lectures on learned
locomotion, imitation, or VLAs use some of these slots and add no homework.
