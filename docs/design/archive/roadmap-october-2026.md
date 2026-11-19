# Introduction to Robotics: requirements and roadmap

**Purpose:** A living outline for an introductory Mechanical Engineering
robotics course and its instructor-maintained repository. Use this document to
plan implementation, carry context into future conversations, and request a
review of comparable courses and reusable teaching resources. It describes
the intended finished course; items marked **open** have not been decided.

**Status (October 2026):** The repository has a Docker Compose scaffold,
student Python and ROS 2 workspace directories, and a ROS 2 Jazzy container
that launched RViz on an Apple Silicon Mac. A small R2D2-like URDF, three
joint sliders, and an RViz view now form the first student installation
exercise. Cross-platform usability and interactive graphics performance
still need evaluation. On the instructor Mac, moving the head slider changed
`/joint_states` and the RViz picture; `/tf` was also present.

## 1. Course goals

- Introduce robotics through mathematics, algorithms, perception, and
  learning, with examples that connect those ideas to robot arms and mobile
  bases.
- Build from small Python exercises toward ROS 2 programs and simulator-based
  demonstrations. The exact assignments and assessments are **open**.
- Give students a repeatable development environment on Windows, Linux, and
  macOS, including both Apple Silicon and Intel Macs.
- Maintain one faculty source for course material and solutions, with a
  deliberate, reviewed process for releasing student-facing code.
- Use outside teaching materials only after instructor review, a check of
  their license or other reuse permission, and attribution in the resulting
  course material.

## 2. Intended learning sequence

| Stage | Required topics | Candidate student activity (to design) |
| --- | --- | --- |
| Foundations | Coordinate frames and basic homogeneous transformations | Compute and visualize frame changes in Python and RViz. |
| Robot-arm geometry | Forward kinematics and Denavit–Hartenberg (DH) parameters | Model a small serial arm and compare calculated and displayed poses. |
| Motion | 2.5D velocity kinematics and arm Jacobians | Relate joint velocities to task-space motion; define precisely what “2.5D” covers for this course. |
| Planning | Basic path-planning algorithms for arms and mobile bases | Compare paths and constraints in simple simulated environments. |
| Perception and feedback | Introductory computer vision, OpenCV, and visual servoing | Detect a visual target and connect image measurements to robot motion. |
| Learned behavior | Basic learned models for vision, then policy learning through reinforcement learning | Train or use a small vision model and apply a learned policy in a bounded simulation task. |

The activities are examples, not yet assignment specifications. Keep the
mathematical foundations understandable to introductory Mechanical
Engineering students; confirm prerequisites and course length before setting
depth or grading scope.

## 3. Student software environment

- Use ROS 2 Jazzy on Ubuntu 24.04 in Docker as the initial common environment.
- Keep Docker Compose as the primary startup method. Consider an optional VS
  Code dev container after the Compose path is reliable; it should reuse the
  same image and workspace.
- Provide separate, persistent places for standalone Python work
  (`student_ws/python/`) and ROS 2 packages (`student_ws/ros2_ws/src/`).
- Select native `linux/arm64` or `linux/amd64` image variants automatically
  through a multi-architecture ROS base. Do not force AMD64 emulation on
  Apple Silicon for the standard path.
- Make at least one simple RViz visualization available to every student.
  The current browser desktop uses software OpenGL as a compatibility
  baseline; measure responsiveness on representative student computers.
- Evaluate a simulator that fits the course and works with ROS 2. Gazebo,
  MuJoCo, and similar options remain candidates. Do not make a simulator a
  student prerequisite until platform support, performance, and teaching
  value are checked.
- Add OpenCV when vision work begins. Consider Stable-Baselines or another
  maintained reinforcement-learning library when the policy exercise is
  specified. These are candidate tools, not committed dependencies today.
- Document setup, startup, common failures, and the limits of graphics
  acceleration for each supported host platform.

## 4. Instructor maintenance and student releases

- Keep the instructor repository as the canonical source for assignments,
  examples, solutions, and future private assessments.
- Keep instructor-only material out of student distributions. A student
  release should be generated into a separate directory from an explicit
  allowlist, inspected, and then published. The release process must not
  modify the instructor working tree.
- Reuse the release-boundary ideas from the sibling
  `byu_robotics_hw_key` repository, adapting them to this course rather than
  copying its assignments or private content.
- Decide how solution regions, notebooks, public checks, and private checks
  will be represented before writing graded exercises. Preserve a clear path
  for semester updates and reviewed improvements.
- When distributing a prebuilt Docker image, publish ARM64 and AMD64 variants
  under the same image tag. Local builds already select the native variant.

## 5. Roadmap and acceptance points

1. **Environment foundation — in progress.** Maintain the Docker image,
   Compose entry point, student workspaces, and a visible RViz startup.
   Use the R2D2-like robot and joint sliders as the first end-to-end check.
   Apple Silicon image build, RViz startup, and head-slider movement have
   been observed. Instructor assessment of responsiveness is still pending.
2. **Platform validation.** Try the same start-to-finish exercise on a
   representative Windows/WSL 2 machine, Linux machine, and Intel Mac.
   Record CPU architecture, Docker version, build result, RViz behavior,
   resource use, and any platform-specific instructions. Establish a modest
   graphics-performance target before requiring complex scenes.
3. **Release boundary.** Implement and review student-release tooling before
   instructor solutions enter student-facing paths. Define an explicit
   allowlist and a repeatable faculty review procedure.
4. **Foundational modules.** Develop transformations, DH/forward kinematics,
   and 2.5D velocity kinematics/Jacobians with small Python and ROS 2
   examples. Reuse suitable material from the existing graduate-level
   robotics course after adjusting depth and prerequisites.
5. **Planning and perception modules.** Add arm and mobile-base planning,
   basic vision, and visual servoing. Choose simple simulated robots and
   scenes that run on supported student machines.
6. **Learning module.** Introduce learned vision models, then a small
   reinforcement-learning policy task. Set realistic compute and runtime
   limits and decide whether training occurs locally or elsewhere.
7. **Course-ready release.** Prepare student documentation, assignments,
   reference visualizations, dependency versions, maintainer instructions,
   and reviewed student artifacts for the first offering.

### Immediate next steps (October 2026)

Work through these in order, using the Mac while it is available and then
continuing on Windows:

1. **Finish the Apple Silicon check.** The startup demo and a head-slider
   movement have been verified on this Mac, including `/joint_states`, `/tf`,
   and the RViz picture. Move both leg sliders, rotate and zoom the scene by
   hand, and record whether browser interaction feels usable for students.
2. **Save the scaffold.** Review the new repository, make its initial commit,
   and push it to a private instructor remote before switching computers.
   The current local `main` branch has no commit or remote yet.
3. **Validate on Windows from a fresh clone.** Use Docker Desktop with WSL 2,
   build and launch the same Compose service, confirm the image is native
   `linux/amd64`, and interact with RViz in the browser. Check that edits in
   both student workspaces persist and that ROS 2 commands work in a
   container shell. Record build time, graphics behavior, and any setup
   changes in the documentation.
4. **Check the remaining host types.** Repeat the basic startup and student
   workflow on representative Linux and Intel Mac machines when available.
   Keep these platforms marked unverified until then.
5. **Pilot a simulator, then select one.** Try a very small scene and ROS 2
   connection with the leading candidates, including Gazebo Harmonic and
   MuJoCo. Compare ARM64/AMD64 availability, ease of teaching, and practical
   performance before adding a simulator to the standard image.
6. **Implement the student release boundary.** Add an explicit allowlist and
   reviewable release-copy process before placing instructor solutions near
   student code or publishing the first student repository.

In parallel, share this roadmap's research brief with ChatGPT Work to find
comparable courses and reusable resources. The instructor will review each
candidate, confirm reuse permission, and approve attribution before adoption.

## 6. Decisions still open

- Course number, length, student prerequisites, learning outcomes at each
  stage, and assessment format.
- Meaning and scope of “2.5D” velocity kinematics in this course.
- Choice of robot arm and mobile-base models, and whether physical hardware
  is used alongside simulation.
- Choice of simulator and ROS 2 integration path, including ARM64 support and
  acceptable graphics performance.
- How much computer vision and reinforcement learning can be taught within
  the course schedule and available student compute.
- Whether VS Code dev containers become a supported convenience layer.
- Student publication channel and license for course-created materials.
- Minimum supported computer specifications and the threshold for an
  acceptable RViz/simulator experience.

## 7. Research brief for ChatGPT Work or another research assistant

Use this document as the course brief. Look for current, publicly available
undergraduate or early graduate robotics courses, labs, textbooks, tutorials,
and software examples that cover the learning sequence above. Favor original
course sites, authors, project documentation, and repositories with clear
reuse terms.

For each promising resource, report:

1. Its source, author/institution, direct link, and license or reuse terms.
2. Which course stage it supports and the expected mathematics/programming
   prerequisites.
3. Whether it includes lecture notes, assignments, starter code, robot
   models, datasets, videos, or instructor-only solutions.
4. Its software versions, operating-system assumptions, ROS/simulator
   dependencies, and maintenance status.
5. The specific idea or asset that could be adapted here, the effort to
   adapt it, and the exact attribution and permission needed.

Compare several options for the simulator and introductory reinforcement
learning stack, especially their ROS 2 Jazzy, ARM64, Windows, and Linux paths.
Separate verified facts from recommendations. Do not copy course solutions or
material without suitable reuse rights. Treat all findings as proposals for
instructor review; do not add them to the course automatically. A useful
output is a topic-by-topic matrix of resources plus a short list of
recommended pilots for this course.

Existing local reference repositories for the instructor to consult are
`byu_robotics_hw_key` (graduate robotics content and student release method),
`marsrover-ros2` (ROS 2/Docker development), and `byu-baxter-lab` (earlier
cross-platform GUI work). They are separate repositories and are not bundled
with this course repository.
