# Draft lecture outlines for planning, vision, and learning

Faculty working draft, November 17, 2026. Each row totals 50 minutes and
adds a specific activity or checkpoint to the instructor's three briefs.
The instructor chose to preserve all six planning slots; the provisional
42-session allocation is in [the integration plan](semester-integration.md).
These are lecture outlines, not completed slides or measured class timings.

## Planning: six proposed lectures

| Session | 50-minute sequence | Active check / preparation |
| --- | --- | --- |
| P1: Configurations and collisions | 10 min point/circular base; 15 min two-joint arm configuration space; 15 min state versus edge validity; 10 min worked example | Use the HW06 activity (faculty master). Students identify why two valid endpoints can still have a colliding connection. |
| P2: RRT-Connect | 5 min one-tree growth; 15 min two trees and connection; 20 min trace a sample and several extensions; 10 min step size, budget, and failure | Hand out a tiny tree with parent indices; students reconstruct the path and check an edge. |
| P3: Transfer to an arm and RRT* | 15 min joint-space scene; 15 min inspect a success and a failed trial; 10 min RRT* parent/rewiring idea; 10 min geometric path versus timed motion | Compare the arm and configuration-space panels. Mark one colliding arm pose on the plot. RRT* is a conceptual comparison. |
| P4: Optimization formulation | 25 min variables, costs, constraints, initial guesses, and local minima; 15 min waypoint formulation; 10 min obstacle-avoidance difficulty | Label the intermediate joint configurations, fixed endpoints, smoothness cost, and collision requirements. |
| P5: Refining a route | 10 min waypoint cost and validity; 15 min CHOMP idea; 10 min provided solver demonstration; 10 min compare initial paths and local methods; 5 min validate output | Ask whether a lower objective proves collision freedom. Show the separate edge check; the simple solver is not CHOMP. |
| P6: Cartesian tasks and position-only optimization | 10 min joint goal versus desired tool path; 20 min working planar example: optimize joint waypoints so the tool hits Cartesian positions, orientation free (D9); 10 min the assigned simplified planar reading of the Bodily, Allen, and Killpack paper; 5 min hard/soft task requirements; 5 min choose a method | Classify a painting waypoint as a hard requirement or a soft cost. Students have implemented damped pseudo-inverse IK (TASKS D5(f)); use it for the painting task. Demo: `python -m examples.position_only_branching --show` (then `--kappa 0` and `--no-obstacle`); reading: [docs/readings/position_only_branching.tex](../readings/position_only_branching.tex). |

All six planning sessions are currently reserved. Keep the shorter combined
outline as a contingency only if the actual holiday/exam calendar removes time.
The P5 base and arm demonstration is the HW07 activity run with the completed
faculty master: `python -m homework.hw07.hw07_optimization --show`. P1--P3 can
use the HW06 activity the same way.

## Computer vision (weeks 8--9)

| Session | 50-minute sequence | Active check / preparation |
| --- | --- | --- |
| 8.1: Camera geometry | 10 min pixels/frames; 15 min pinhole projection and depth ambiguity; 15 min intrinsics, pose, and distortion; 10 min plane mapping | Project one camera-frame point by hand and explain why one pixel alone does not determine depth. |
| 8.2: Homography and features | 20 min fit/validate a plane map; 20 min segmentation and contour measurements; 10 min oblique-scene exercise | Use four known marks and the separate fifth check. Predict the effect of applying a plane map to a feature above the plane. |
| 8.3: Tracking and velocity | 10 min mask robustness; 10 min association; 10 min timestamps; 10 min metric velocity and failures; 10 min conveyor sequence | Estimate velocity from two positions and actual times; distinguish missing detection from a measurement at the origin. |

Prepare the perspective-correct pilot, calibration pairs, held-out check,
and a sequence with timestamps before the unit. The OpenCV version of this
material still needs implementation and compatibility testing.

## Visual servoing (weeks 9--10)

| Session | 50-minute sequence | Active check / preparation |
| --- | --- | --- |
| 9.1: Planar feedback | 10 min fixed-camera features/error; 15 min plane mapping and planar robot Jacobian; 15 min velocity feedback; 10 min worked example | Given target and tool positions in one frame, predict the error and direction of a bounded command. |
| 9.2: Camera on the tool | 15 min camera-to-tool frames and moving view; 15 min provided image sensitivity and depth; 10 min demonstration; 10 min feature count and task limits | Predict the image motion caused by a small camera motion; explain why the fixed-camera map changes. |
| 9.3: Integration and limits | 15 min run/inspect a servo example; 15 min gain, delay, saturation, and lost feature; 10 min compare image/position feedback; 10 min review | Given a lost target, choose a safe hold/stop response. Discuss large commands near difficult poses without assigning singularity analysis. |

A fixed-camera host pilot produces stationary-target feedback, and a separate
moving-object example demonstrates a timed pickup with image-derived velocity.
They still need an OpenCV-backed, student-ready exercise. A tool-camera image
is available, but a closed-loop eye-in-hand demonstration still has to be
built. A full spatial Jacobian
derivation is outside this course's velocity scope. Instructor decision,
November 19: tool-camera IBVS is required for every student, so these three
sessions are being reworked around it (TASKS.md open work).

## Supervised learning and PyTorch (weeks 10--11)

| Session | 50-minute sequence | Active check / preparation |
| --- | --- | --- |
| 10.1: Supervised perception | 10 min conveyor pipeline; 15 min input/label; 15 min grouped splits and overfitting; 10 min inspect crops | Decide whether adjacent frames from one scene belong in different splits, and explain why. |
| 10.2: One training update | 10 min tensors/preprocessing; 15 min supplied model, scores, and loss; 15 min gradients/optimizer; 10 min trace a batch | Label the image and output shapes; identify what changes when the optimizer steps. |
| 10.3: Train and evaluate | 15 min prepared training/checkpoint; 15 min held-out errors; 10 min simple-rule baseline; 10 min use a label in the pipeline | Inspect a mistaken crop and explain whether the failure came from segmentation, classification, or both. |

Prepare balanced shapes/colors, grouped scene identifiers, consistent RGB
preprocessing, a small CPU-sized model, a trained fallback, and independent
test scenes. The current six-frame pilot is not a classifier dataset.

## Reinforcement learning (weeks 11--12)

| Session | 50-minute sequence | Active check / preparation |
| --- | --- | --- |
| 11.1: RL as feedback | 10 min control goal; 15 min observation/action/environment; 15 min reward/return/episodes; 10 min robot or provided example | Identify measured observations and bounded actions; distinguish a time limit from task termination. |
| 11.2: Policies and SB3 | 15 min policy/value intuition; 10 min PPO idea; 15 min prepared SB3 experiment; 10 min inspect the PyTorch policy | Trace observation to action and explain what the network represents. No PPO derivation or implementation is assigned. |
| 11.3: Evaluate and choose | 15 min evaluate a prepared agent; 15 min baseline/failures; 10 min seeds and simulation-to-real; 10 min project choices | Interpret success and failures together with return. Explain why a reward can be an imperfect task measure. |

Prefer a prepared planar reaching environment if a working one is piloted;
otherwise use a supplied small control example and a conceptual robot
comparison. A checkpoint and recorded results protect the lecture if training
is slow. Imitation of visual servoing and RL improvement are optional project
extensions, not required week-11 work.

## Project weeks 12--14

- **Week 12:** use the fixed-camera HW09 result as preparation, then demonstrate
  calibration and a bounded approach with the team's selected camera.
- **Week 13:** integrate moving-object interception, timed pickup, transfer,
  and bins; test under common scenarios with the selected camera.
- **Week 14:** evaluate held-out cases, explain failures and design tradeoffs,
  and demonstrate the integrated solution or an approved extension.

These milestones depend on providing the project simulator and baseline
beforehand. Optional one-to-three lectures on learned locomotion, imitation,
or VLAs use some of these project slots and add no homework.
