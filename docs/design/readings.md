# Readings and outside resources

Faculty working draft, November 25, 2026. Nothing here is approved until
TASKS.md item R14 records instructor review. This is the topic-by-topic
resource matrix that the [roadmap](../../COURSE_ROADMAP.md#open-decisions-and-outside-resources)
asks for. It sorts every outside resource into one of three tiers, so the
syllabus can say plainly what every student reads.

| Tier | Who | What it means |
| --- | --- | --- |
| **Read** | Every student, before the listed session | Short and assigned. Reading points are for completion only (instructor, Nov 25); the instructor sets how completion is recorded. About 100 textbook pages in all, plus seven short web pages or sections, spread over 13 weeks. |
| **Reference** | Students who want more | Optional. Listed in each homework README or lecture slide where it helps; never needed to finish an assignment. |
| **Faculty** | Instructor and TAs | Lecture preparation and checking. Often graduate level; not given to students as reading. |

**Required text: Corke, *Robotics, Vision and Control: Fundamental Algorithms in
Python*, 3rd ed. (Springer, 2023)** (instructor decision, Nov 25). BYU students get
the e-book free through the library's SpringerLink subscription (sign in through the
library off campus). Suggested syllabus wording:

> **Required text.** Peter Corke, *Robotics, Vision and Control: Fundamental
> Algorithms in Python*, 3rd ed. (Springer, 2023). The e-book is free to BYU
> students through the Harold B. Lee Library's SpringerLink access; search the
> library catalog for the title and sign in with your BYU NetID off campus. You
> do not need to buy a copy. Weekly readings are listed with each lecture.

 Page
numbers below are the printed book pages; section numbers match the SpringerLink
chapter PDFs. Tell students to read for the ideas and figures: the book's
code calls Corke's own Toolboxes (`spatialmath`, `roboticstoolbox`,
`machinevisiontoolbox`), while their homework is written in NumPy and OpenCV. The
Toolboxes are fine for checking answers.

Notation: Corke writes a relative pose as a symbol with the reference frame
before it and the target frame after it, read "the pose of B relative to A". That
is the same idea as the course's `t_w_c` names. Say so in lecture 1.3.

Copyright: link to every resource; do not copy text, figures, or a PDF of any
book into this repository or the student copy. The instructor's copy of the
Corke PDF stays outside the repository.

## Required reading, in session order

Sessions use the `week.meeting` numbering and lecture codes of the
[session calendar](semester-integration.md). A reading is due before the
session it is listed with.

| # | Before | Topic | Read | Length |
| --- | --- | --- | --- | --- |
| 1 | 1.2 | ROS 2 graph | ROS 2 Jazzy tutorials [Understanding nodes](https://docs.ros.org/en/jazzy/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Nodes/Understanding-ROS2-Nodes.html) and [Understanding topics](https://docs.ros.org/en/jazzy/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Topics/Understanding-ROS2-Topics.html). Read the explanations; the turtlesim commands are optional (students run ROS in the course container, not a native install). | 2 web pages |
| 2 | 1.3 | Frames and relative pose | Corke 2.1 Foundations (relative pose, coordinate frames, pose graphs) | pp. 24--31 (8) |
| 3 | 2.1 | Rotation matrices | Corke 2.2.1.1 2D rotation matrix; 2.3.1.1 3D rotation matrix. Stop at the matrix exponential sections. | pp. 33--35, 46--48 (6) |
| 4 | 2.3 | Homogeneous transforms | Corke 2.2.2.1--2.2.2.2 2D homogeneous transform and rotating a frame; 2.3.2.1 3D homogeneous transform | pp. 36--41, 61--63 (9) |
| 5 | 3.3 | Forward kinematics | Corke 7.1.1 FK from a pose graph; 7.1.2 FK as a chain of links, including 7.1.2.3 tools and bases. Skip 7.1.5 (DH stays in ME 537). | pp. 256--268 (13) |
| 6 | 4.1 | Roll-pitch-yaw and URDF | Corke 2.3.1.2, only the roll-pitch-yaw part through Eq. 2.23: yaw about Z, then pitch about the new Y, then roll about the new X, R = Rz Ry Rx. This is the course's current-frame reading of URDF origins; skip Corke's XYZ variant. Then Corke 7.1.4 URDF. | pp. 50--51, 270--274 (7) |
| 7 | 4.3 | Manipulator Jacobian | Corke 8.1 intro and 8.1.1 Jacobian in the world frame. The course uses the planar 3-by-n case; the idea is the same. | pp. 308--311 (4) |
| 8 | 5.3 | Interpreting the Jacobian | Corke 8.3 intro, 8.3.1 singularities, 8.3.2 velocity ellipsoid and manipulability (the arm viewer draws these ellipses) | pp. 315--320 (6) |
| 9 | 6.1 (IK1) | Inverse kinematics and damped least squares | Corke 7.2.1 planar IK (closed form shows the two elbow solutions; then numerical); 8.3.3 dealing with Jacobian singularity (damped inverse); 8.3.4 non-square Jacobians (redundant arm) | pp. 278--281, 320--324 (8) |
| 10 | 6.2 (P1) | Configuration space and RRT | Dellaert and Hutchinson, [*Introduction to Robotics and Perception*, Sec. 5.5](https://www.roboticsbook.org/S55_diffdrive_planning.html): 5.5.1 configuration-space obstacles, 5.5.5 RRTs, 5.5.6 RRT implementation. Skim 5.5.2--5.5.4. | 1 web section |
| 11 | 8.1 (P6) | Position-only optimization | Course reading [`position_only_branching.tex`](../readings/position_only_branching.tex) (already assigned under D9) | 3 |
| 12 | 8.2 (V1) | Pinhole camera | Corke 13.1.1--13.1.5 perspective projection through projecting points. Skip 13.1.6 lens distortion. | pp. 540--551 (12) |
| 13 | 8.3 (V2) | Homography, segmentation, shape | Corke 13.6.2 planar homography; 12.1.2 intro and 12.1.2.1 binary blobs; 12.1.3.1--12.1.3.3 area, bounding boxes, moments. Then OpenCV [Changing Colorspaces](https://docs.opencv.org/4.x/df/d9d/tutorial_py_colorspaces.html) (HSV and `inRange`, as in HW08). | pp. 578--579, 492--494, 496--499 (9) + 1 web page |
| 14 | 9.2 (VS1) | Visual servoing: measure-then-move versus image-based | Corke 15.1 position-based servoing (read for the contrast, not the details); 15.2.1 camera and image motion (the image Jacobian) | pp. 669--679 (11) |
| 15 | 9.3 (VS2) | IBVS control law | Corke 15.2.2 controlling feature motion | pp. 679--684 (6) |
| 16 | 10.2 (L1) | Training loop | PyTorch tutorial [Optimizing Model Parameters](https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html) (hyperparameters, loss, the train and test loops) | 1 web page |
| 17 | 10.3 (L2) | Honest evaluation | scikit-learn [Common pitfalls](https://scikit-learn.org/stable/common_pitfalls.html), the Data leakage section only. Lecture extends it to scene-grouped splits. | 1 web section |
| 18 | 11.3 (RL1) | RL vocabulary | OpenAI Spinning Up, [Part 1: Key Concepts in RL](https://spinningup.openai.com/en/latest/spinningup/rl_intro.html): "What Can RL Do?" and "Key Concepts and Terminology". Skip "(Optional) Formalism". | 1 web page |

No reading is assigned for tracking and velocity (9.1), which is a least-squares
line fit from numerical methods; for the project launch (PL1--PL2), where the
reading is the project's own [student guide](../../homework/project/README.md);
or for PPO (12.1), which lecture teaches as intuition only.

The full list stands for now (instructor, Nov 25). Instructor option if it
proves too long for completion points: drop readings 2, 8, 15, and 17 first,
since lecture covers each of them.

## Resource matrix by course outcome

Numbers in the Read column refer to the table above. Corke sections are
"C"; Dellaert and Hutchinson "DH"; Tedrake's *Robotic Manipulation* "T".

| Outcome | Read | Reference (students) | Faculty |
| --- | --- | --- | --- |
| 1. ROS 2 | 1 | ROS 2 Jazzy tutorials: [tf2](https://docs.ros.org/en/jazzy/Tutorials/Intermediate/Tf2/Tf2-Main.html) "Introducing tf2" and "Writing a static broadcaster (Python)" (HW03); URDF "Using URDF with robot_state_publisher (Python)" (HW04). Herath and St-Onge, *Foundations of Robotics*, Ch. 5 (ROS 1 and 2). | The course [setup](../setup.md) and HW01 handout remain the primary ROS material. |
| 2. SO(3) and SE(3) | 2, 3, 4, 6 | C 2.3.1.3 gimbal lock (pp. 52--54); C 2.4.1--2.4.2 pre- versus post-multiplication (pp. 67--68; warn that the course teaches only current-frame composition); T Ch. 3 [monogram notation and spatial algebra](https://manipulation.mit.edu/pick.html#monogram) (frame-subscript names like `t_w_c`). | Lynch and Park, *Modern Robotics*, Ch. 3. |
| 3. Serial-linkage kinematics | 5, 6, 9 | C 7.1.3 branched robots (pp. 268--270); C 7.2.4 redundant manipulators (pp. 284--285); C 8.5 numerical IK (pp. 325--327); T Ch. 3 [forward kinematics](https://manipulation.mit.edu/pick.html#kinematics); T Ch. 6 [inverse kinematics](https://manipulation.mit.edu/trajectories.html#section1). | Lynch and Park Ch. 4 and 6 (product of exponentials, Newton--Raphson IK); Siciliano et al. Ch. 2. |
| 4. Velocity kinematics | 7, 8, 9 | C 8.2 resolved-rate motion control (pp. 313--315; the same loop as HW09); T Ch. 3 [Jacobians](https://manipulation.mit.edu/pick.html#jacobian), [differential IK](https://manipulation.mit.edu/pick.html#section6), and [with constraints](https://manipulation.mit.edu/pick.html#diff_ik_w_constraints). | Lynch and Park Ch. 5 (twists); Siciliano et al. Ch. 3. |
| 5. Path planning | 10, 11 | T Ch. 6 [kinematic trajectory optimization](https://manipulation.mit.edu/trajectories.html#section2) and [sampling-based planning](https://manipulation.mit.edu/trajectories.html#section3); LaValle, *Planning Algorithms*, [Sec. 5.5](https://lavalle.pl/planning/node230.html) (RRTs, including the bidirectional version); DH 5.5.4 PRMs; C 5.5 roadmaps and 5.6.5 planning in configuration space (pp. 184--188, 196--199); C 7.5.5 collision detection (pp. 301--303). | Kuffner and LaValle, "RRT-Connect" (ICRA 2000); Bodily, Allen, and Killpack (ICRA 2017); Lynch and Park Ch. 10; Siciliano et al. Ch. 12. |
| 6. Computer vision | 12, 13 | C 13.2.2 checkerboard calibration (pp. 550--553; the PL1 checkoff); C 14.2.4 estimating a homography from points (pp. 604--610); C 12.1.1.2 color classification (pp. 486--491); C 12.1.3.7 shape from perimeter (pp. 505--508); C 11.6.1 morphological noise removal (pp. 464--465); C 10.2.7 color spaces (pp. 396--399); [OpenCV 4.x documentation](https://docs.opencv.org/4.x/) for `findHomography`, contours, and `approxPolyDP`. | C Appendix H, Kalman filter (p. 762), if filtered velocity grows beyond a line fit. |
| 7. Visual servoing | 14, 15 | C 15.2.3 estimating feature depth and 15.2.4 performance issues (pp. 684--688; gain and sampling); Chaumette and Hutchinson, "Visual servo control, Part I" (2006), [author copy on HAL](https://hal.archives-ouvertes.fr/inria-00350283). | Siciliano et al. Ch. 10; Spong, Hutchinson, and Vidyasagar, 2nd ed., Ch. 11 (purchase only). |
| 8. Classification | 16, 17 | DH [5.6](https://www.roboticsbook.org/S56_diffdrive_learning.html) supervised learning in PyTorch (5.6.1--5.6.5); C 12.1.1.3 semantic classification and 12.1.4 detection with deep learning (pp. 491--492, 508--509); T Ch. 9 [object detection and segmentation](https://manipulation.mit.edu/segmentation.html) (advanced). | -- |
| 9. Reinforcement learning | 18 | DH [3.6](https://www.roboticsbook.org/S36_vacuum_RL.html) value iteration and Q-learning (tabular, with code) and [6.6](https://www.roboticsbook.org/S66_driving_DRL.html) deep RL (brief); Stable-Baselines3 [RL Tips and Tricks](https://stable-baselines3.readthedocs.io/en/master/guide/rl_tips.html) (limits of RL, evaluating on separate cases); Spinning Up [PPO](https://spinningup.openai.com/en/latest/algorithms/ppo.html) (mathematical); T Ch. 11 [Reinforcement Learning](https://manipulation.mit.edu/rl.html) (advanced). | -- |
| 10. Integration | -- | T Ch. 3 [a pick and place trajectory](https://manipulation.mit.edu/pick.html#pick_and_place_trajectory) and [putting it all together](https://manipulation.mit.edu/pick.html#section9); for the extension lectures, DH 5.6.6 (transformers and vision-language-action models) and T Ch. 10 [deep perception](https://manipulation.mit.edu/deep_perception.html). | -- |

## Resource register

The roadmap's outside-resource policy asks for source, access, and reuse terms.
Every resource is **linked, not copied**; any figure or problem adapted into a
handout needs the owner's permission and a citation.

| Resource | Author, publisher | Access and license | Software | Tier |
| --- | --- | --- | --- | --- |
| *Robotics, Vision and Control: Fundamental Algorithms in Python*, 3rd ed. (2023), [book page](https://petercorke.com/rvc3p/home/) | Peter Corke; Springer (STAR 146) | E-book free to BYU through SpringerLink; print for purchase. Example code: [RVC3-python](https://github.com/petercorke/RVC3-python), MIT license. | Python Toolboxes; notebooks run on Colab | Read (primary text) |
| [*Introduction to Robotics and Perception*](https://www.roboticsbook.org/) | Frank Dellaert and Seth Hutchinson | Free online; notebook source on GitHub ([gtbook/robotics](https://github.com/gtbook/robotics)), BSD-3 | Python, GTSAM, PyTorch | Read (planning); Reference |
| [*Robotic Manipulation*](https://manipulation.mit.edu/) course notes | Russ Tedrake, MIT | Free online; copyright the author | Drake (pydrake), Colab | Reference |
| ROS 2 Jazzy [tutorials](https://docs.ros.org/en/jazzy/Tutorials.html) | Open Robotics and contributors | Free online | ROS 2 Jazzy (the course image) | Read; Reference |
| PyTorch [tutorials](https://docs.pytorch.org/tutorials/beginner/basics/intro.html) | PyTorch Foundation | Free online | PyTorch | Read |
| scikit-learn [Common pitfalls](https://scikit-learn.org/stable/common_pitfalls.html) | scikit-learn developers | Free online | scikit-learn (not used in the course; read for the idea) | Read |
| OpenAI [Spinning Up](https://spinningup.openai.com/) | Joshua Achiam, OpenAI | Free online | Not used | Read; Reference |
| Stable-Baselines3 [documentation](https://stable-baselines3.readthedocs.io/) | SB3 contributors | Free online; SB3 is MIT licensed | Stable-Baselines3 (the course's RL tool) | Reference |
| OpenCV [4.x documentation](https://docs.opencv.org/4.x/) | OpenCV team | Free online | OpenCV (the course's vision tool) | Read; Reference |
| [*Foundations of Robotics*](https://link.springer.com/book/10.1007/978-981-19-1983-1) (2022) | Damith Herath and David St-Onge, eds.; Springer | Open access, CC BY-NC-ND 4.0 | Python, ROS 1 and 2 | Reference |
| [*Planning Algorithms*](https://lavalle.pl/planning/) (2006) | Steven LaValle; Cambridge | Free online | -- | Reference |
| "Visual servo control, Part I: Basic approaches," *IEEE Robotics and Automation Magazine* 13(4), 2006 | François Chaumette and Seth Hutchinson | Author copy free on [HAL](https://hal.archives-ouvertes.fr/inria-00350283); journal through the BYU library | -- | Reference; Faculty |
| *Robotics: Modelling, Planning and Control* (2009) | Siciliano, Sciavicco, Villani, and Oriolo; Springer | Free to BYU through SpringerLink | -- | Faculty. Graduate level (instructor, Nov 25); useful for checking derivations. |
| [*Modern Robotics*](https://hades.mech.northwestern.edu/index.php/Modern_Robotics) (2017) | Kevin Lynch and Frank Park; Cambridge | Free preprint for personal use; videos on Coursera | MR code library | Faculty. Built on screw theory and exponential coordinates, which the course leaves out. |
| *Robot Modeling and Control*, 2nd ed. (2020) | Spong, Hutchinson, and Vidyasagar; Wiley | Purchase | -- | Faculty. Built on DH. |

Considered and not used: Correll et al., *Introduction to Autonomous Robots*
(MIT Press, 2022; short, with no visual servoing or RL); Hauser, *Robotic
Systems* (free draft whose perception and learning chapters are marked
incomplete); and *Robotics Programming with Python* (independently published
2026, ISBN 9798197715807; no academic authorship or review record found).

## Gaps

- **ROS 2:** no textbook teaches ROS 2 Jazzy well; the official tutorials and
  the course's own setup and HW01 materials are the source.
- **Arm planning:** Corke's planning chapter is about mobile robots; Dellaert and
  Hutchinson cover RRT for a point robot. RRT-Connect and waypoint optimization
  for an arm come from lecture, the D9 reading, and the Tedrake references.
- **Damped least squares:** Corke 8.3.3 introduces the damped inverse but
  briefly; lecture IK1 remains the main source, and it is where the course's
  point that damping is numerical, not physical, must be made.
- **Velocity from timestamps** is a numerical-methods fit, with no reading.
