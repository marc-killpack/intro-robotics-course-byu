# Introductory robot path planning: two-week course design

## Purpose and status

This is a working course-design brief for an introductory robotics course in the Brigham Young University mechanical engineering department. It is intended to give another Codex session the context needed to help develop course materials in an existing repository.

The planned unit is **two weeks, with six 50-minute lectures**:

1. One week on configuration space, collision checking, and sampling-based planning.
2. One week on optimization-based motion planning and its connection to task-space motion.

The main application is **collision-aware path planning for articulated robot arms**. An idealized 2D mobile-base example provides an accessible introduction before extending the same ideas to arm configuration space. Broader manipulation topics such as grasp selection and task planning are outside the central scope.

These are proposed unit outcomes, teaching activities, and implementation choices, not finalized syllabus requirements. The instructor has expressed particular interest in **RRT-Connect**, a conceptual introduction to **RRT\***, and a meaningful introduction to **optimization-based planning**. The [Bodily, Allen, and Killpack paper](https://scholarsarchive.byu.edu/facpub/3204/) is an **optional** task-space example.

### Guidance for the receiving Codex session

- Check the existing repository structure, course goals, languages, tools, and applicable instructions before proposing additions.
- The instructor wants student-repository changes tracked and approved rather than made implicitly. Determine whether the repository is a student repository; if that is unclear, ask what the code is for. Prepare concrete, reviewable changes and follow the applicable approval instructions.
- Treat the lecture plan, learning outcomes, assessment ideas, and software choices in this document as proposals to adapt with the instructor. Do not assume that a specific framework, assignment, or paper has already been approved.
- Keep the teaching focus on student capabilities as well as conceptual understanding.

## Audience, prerequisites, and scope

The unit is aimed at introductory undergraduate or graduate students, with particular relevance to mechanical engineering. The proposed programming work assumes that students have some familiarity with arrays, functions, plotting, and the robot kinematics introduced earlier in the course.

Assumed supporting material:

- Forward kinematics and the notion of inverse kinematics have already been introduced.
- A simple robot model, obstacle representations, visualization, and collision-checking functions are provided for programming exercises.
- A numerical optimizer is provided or already available through the course software.
- A short assignment or lab outside the six lectures is available. If not, replace implementation outcomes with guided use and tracing of provided code.

The initial mobile-base model is an idealized point or circular robot in a planar environment. For a circular footprint, obstacles may be expanded by the robot radius. A path in just position coordinates does not automatically account for heading, turning constraints, or nonholonomic motion. Introduce those limitations without requiring a full mobile navigation unit.

For an arm, plan in joint configuration space. A configuration describes the entire robot, not just its end effector. Collision checks must account for the links, the environment, and self-collision where applicable. Joint limits, angle wraparound, distance metrics, and interpolation all affect a practical implementation.

## Proposed core learning outcomes

By the end of the unit, students should be able to:

| ID | Proposed outcome | Possible evidence |
| --- | --- | --- |
| LO1 | **Represent** a simple mobile-base or robot-arm planning problem in configuration space, including its start, goal, joint limits, and obstacles. | Given a two-joint arm and a scene, identify the configuration variables and relate a point in configuration space to a physical arm pose. |
| LO2 | **Evaluate** whether a proposed configuration-space path is valid for a given robot and obstacle model. | Identify collisions or joint-limit violations, check intermediate configurations, and explain the limitation of the chosen checking resolution. |
| LO3 | **Implement RRT-Connect** for a simple 2D configuration-space problem using provided sampling, collision-checking, and visualization functions. | Demonstrate two trees growing and connecting for an idealized mobile base, then use the same planner interface with a provided two-joint arm model. |
| LO4 | **Formulate** a kinematic waypoint-optimization problem by identifying its decision variables, objective, and constraints. | Write a problem that favors smooth joint motion between endpoints while respecting limits and avoiding obstacles. Identify the initial guess separately from the requirements. |
| LO5 | **Use** a provided optimization tool to refine a candidate path for a specified objective and constraints. | Run the tool, interpret its result, and check the candidate for goal satisfaction and collisions. Diagnose solver failure or an invalid result when it occurs. |
| LO6 | **Analyze** the performance of planning methods using evidence from simulated trials. | Compare valid-path rate, planning time, and path quality; include failed runs and explain the effects of randomness or initialization. |
| LO7 | **Justify** a planning approach for a specified robot task using the task requirements and the strengths and limitations of the methods studied. | Recommend a method or combination for an arm moving around obstacles or for a task with a prescribed Cartesian tool path. State the assumptions. |

If students will not implement a planner, revise LO3 to: **Use and trace RRT-Connect in a provided planning tool.** This changes the expected skill and should be reflected in assessment.

### Optional outcomes

- **Trace** RRT\* parent selection and rewiring in a small example, and explain the meaning of continued improvement in path cost.
- **Distinguish** a geometric path from a timed trajectory, and identify why velocity limits or dynamics require additional information.
- **Express** a desired Cartesian end-effector pose or path as a goal, constraint, or cost on joint configurations.
- **Explain** how CHOMP adjusts an initial trajectory using smoothness and obstacle costs, and why different initial guesses can lead to different results.
- **Identify** what must be added to a kinematic planning problem to account for dynamics, such as states, controls, equations of motion, and actuator limits.

These are unit-level outcomes. They may contribute evidence toward broader ABET engineering outcomes concerning problem formulation, experimentation, and engineering judgment, but they do not by themselves establish attainment of program-level outcomes. See [ABET's 2026–2027 engineering criteria](https://www.abet.org/accreditation/accreditation-criteria/criteria-for-accrediting-engineering-programs-2026-2027/).

## Six-lecture outline

The times below total 50 minutes per lecture and can be adapted to the existing course schedule.

| Lecture | Proposed sequence | Capability emphasized |
| --- | --- | --- |
| **1. Configuration space and collisions** | **10 min:** 2D base and obstacles. **15 min:** configuration space for a two-joint arm. **15 min:** checking configurations and motions between them. **10 min:** worked example. | Model the problem and recognize why valid endpoints alone do not ensure a valid path. |
| **2. RRT-Connect** | **5 min:** basic single-tree RRT growth. **15 min:** two trees and the connect operation. **20 min:** trace and visualize a 2D example. **10 min:** sampling, step size, and failure. | Trace and explain the algorithm and its collision checks. |
| **3. Arm planning and RRT\*** | **15 min:** apply RRT-Connect to a two-joint arm. **15 min:** demonstrate planning and diagnosing a failure. **10 min:** RRT\* parent selection and rewiring. **10 min:** path quality and path versus timed trajectory. | Transfer the method from a mobile-base example to arm joint space; recognize feasible versus improved paths. |
| **4. What is optimization?** | **25 min:** variables, costs, constraints, feasibility, initial guesses, and local minima. **15 min:** formulate waypoint optimization. **10 min:** why obstacle avoidance can make the problem difficult. | Read and formulate an optimization problem without learning how to implement a solver. |
| **5. Trajectory optimization and CHOMP** | **10 min:** waypoint costs and collision constraints. **15 min:** CHOMP's basic update idea. **10 min:** demonstrate an initial and optimized path. **10 min:** conceptual comparison with TrajOpt and STOMP. **5 min:** validate the result. | Explain what an optimizer changes and assess whether its result meets the task requirements. |
| **6. Cartesian tasks and future extensions** | **15 min:** joint-space goals versus prescribed Cartesian paths. **10 min:** discuss the Bodily, Allen, and Killpack paper if selected, or another task-space example. **10 min:** formulate task objectives and constraints. **10 min:** preview dynamics. **5 min:** compare method choices. | Choose or combine methods for different task specifications and identify a path toward dynamic trajectory optimization. |

For quick in-class practice, students could trace one RRT-Connect iteration, identify a collision between two valid endpoints, label the variables and constraints of an optimization problem, or predict how changing an initial guess could affect a local optimizer. An engineering education review reports broad but uneven support for active, collaborative, and problem-based approaches: [Prince, 2004](https://onlinelibrary.wiley.com/doi/10.1002/j.2168-9830.2004.tb00809.x).

## Method options and tradeoffs

The following approaches solve related but different problems. The comparison identifies useful teaching connections; it does not claim that one method is an industry-wide standard or that a single method is best for every scene.

| Approach | How it is used and why it is useful | Main tradeoff or limitation |
| --- | --- | --- |
| **RRT-Connect** | Grows one tree from the start and another from the goal. It combines random exploration with a greedy attempt to connect the trees, often finding a feasible geometric path quickly. | Aimed at feasibility rather than continually improving path cost. Performance depends on the scene and planning budget; a finite run can fail. [Original paper](https://www.clear.rice.edu/comp450/papers/kuffner_lavalle_00.pdf) |
| **RRT\*** | Uses nearby nodes to choose a lower-cost parent for a new node and rewires neighbors when the new route lowers their cost. | More neighbor searches and collision checks than basic RRT. The standard formulation is a separate single-tree method, not simply RRT-Connect with rewiring. Its optimality result is asymptotic under assumptions, not a finite-time guarantee. [Original paper](https://dspace.mit.edu/entities/publication/77dff1d1-ffd6-42f3-a3a5-fef87a964959) |
| **Waypoint optimization** | Treats intermediate configurations as decision variables and minimizes a chosen path-quality cost subject to task and validity requirements. A general-purpose numerical solver can be used. | A clear first optimization problem and a bridge to other methods. Collision avoidance and nonlinear forward kinematics can make the problem nonconvex; a local solver can fail or depend on its initial guess. |
| **CHOMP** | Uses gradient-based updates to improve an initial trajectory using smoothness and obstacle costs. It can start from an interpolated trajectory or from a path produced by a planner. | Makes path-quality objectives explicit, but can get stuck in a poor local solution. Collision penalties and discretization do not remove the need to validate the final path. [CHOMP paper](https://personalrobotics.cs.washington.edu/publications/zucker2013chomp.pdf) |
| **TrajOpt** | Uses sequential convex optimization: repeatedly approximate the current trajectory-planning problem locally and solve a simpler subproblem. It supports kinematic and collision-related costs and constraints. | A useful introduction to constrained local optimization, but its numerical details are more involved than a first waypoint example. Initialization and local minima remain important. [Original paper](https://people.eecs.berkeley.edu/~pabbeel/papers/2014-IJRR-trajopt.pdf) |
| **STOMP** | Generates noisy variants of a trajectory, evaluates their costs, and uses them to update the trajectory without requiring cost gradients. | Can handle some nondifferentiable costs; it needs multiple trajectory evaluations and can still depend on its initial guess. Its sampling explores trajectories around a candidate, rather than growing an RRT. [MoveIt guide](https://moveit.picknik.ai/main/doc/how_to_guides/stomp_planner/stomp_planner.html) |
| **QP-based task-space motion / inverse kinematics** | Chooses robot configurations or motion to follow desired Cartesian targets while satisfying limits and balancing objectives. The optional Bodily, Allen, and Killpack example jointly plans base position and arm motion along a desired end-effector trajectory. | Particularly useful when the task already specifies where the tool should move. The requested Cartesian motion can itself be infeasible; the method does not automatically find a different task path in every scene. [BYU paper record](https://scholarsarchive.byu.edu/facpub/3204/) |
| **GPMP2** | Represents a trajectory with a Gaussian process and uses factor-graph inference and numerical optimization to address smoothness and obstacle avoidance. | An established research option, but Gaussian processes and factor graphs add concepts that are difficult to justify in this short unit. [GPMP2 paper](https://homes.cs.washington.edu/~bboots/files/GPMP2.pdf) |
| **Direct trajectory optimization / direct collocation** | Optimizes states and controls while adding constraints based on the system's equations of motion. Can incorporate torque, timing, balance, and contact-related considerations. | A strong bridge toward dynamic and humanoid robotics, but requires more modeling and optimization background. Direct collocation is a formulation technique, not one particular solver. [MIT notes](https://underactuated.csail.mit.edu/trajopt.html) |
| **Whole-body quadratic programming** | Coordinates multiple tasks and constraints, such as end-effector motion, balance, contacts, and joint limits, often at control rate. | Relevant to humanoids and whole-body motion generation, but it is generally a control or motion-generation component rather than a standalone global path planner. [Atlas full-body control paper](https://onlinelibrary.wiley.com/doi/abs/10.1002/rob.21559) |
| **Industrial PTP, LIN, and CIRC motions** | Generate familiar point-to-point, linear Cartesian, or circular Cartesian motions, often with timing and blending. | Useful practical motions when the desired path is known. They are not general optimization-based obstacle-route planners. [Pilz documentation](https://moveit.github.io/moveit_tutorials/doc/pilz_industrial_motion_planner/pilz_industrial_motion_planner.html) |

### Priorities for this short course

| Priority | Topic or method | Suggested depth |
| --- | --- | --- |
| **Core** | Configuration space, robot geometry, state and motion validity | Work examples for a 2D base and a two-joint arm. |
| **Core** | RRT-Connect | Trace the algorithm and implement or use it with provided collision and visualization tools. |
| **Core** | Optimization formulation | Identify variables, objective, hard constraints, initial guess, feasibility, and local minima. |
| **Core** | Waypoint optimization and one practical optimizer | Formulate and run a small example with a supplied solver. Use CHOMP as a named practical illustration if supported by the course tools. |
| **Core** | Validation and comparison | Inspect path validity, failures, path quality, and computation time. |
| **Brief** | RRT\* | Explain lower-cost parent selection, rewiring, and the idea of asymptotic improvement. |
| **Brief** | TrajOpt and STOMP | Compare their central ideas with CHOMP; do not require implementations. |
| **Optional** | Bodily, Allen, and Killpack paper | Use as a task-space application or optional reading, not a required paper unless the instructor chooses it. |
| **Preview** | Direct collocation and whole-body optimization | Show how states, controls, dynamics, and contacts extend the formulation. |
| **Optional reference** | GPMP2 and industrial motion primitives | Mention where useful for future study or application context. |

## A simple optimization formulation

Let a discretized arm path contain configurations \(q_0,\ldots,q_N\). The fixed start and goal are \(q_{\mathrm{start}}\) and \(q_{\mathrm{goal}}\). Choose the intermediate configurations to minimize changes between successive waypoint steps:

\[
\begin{aligned}
\underset{q_1,\ldots,q_{N-1}}{\operatorname{minimize}} \quad &
\sum_{i=1}^{N-1}\left\|q_{i+1}-2q_i+q_{i-1}\right\|^2 \\
\text{subject to} \quad &
q_0=q_{\mathrm{start}},\qquad q_N=q_{\mathrm{goal}}, \\
& q_{\min}\leq q_i\leq q_{\max}, \\
& d_j(q_i)\geq \delta_j
\quad\text{for the relevant collision pairs }j.
\end{aligned}
\]

Here \(d_j\) is an appropriate signed distance for a robot–environment or self-collision pair, and \(\delta_j\) is a required clearance. The collision requirements are shown at the discrete waypoints; the connecting motions must also be checked.

Students should be able to identify:

- **Decision variables:** the intermediate joint configurations.
- **Objective:** the chosen measure of variation between successive waypoint steps.
- **Constraints:** fixed endpoints, joint limits, and collision or clearance requirements.
- **Initial guess:** a candidate waypoint sequence, such as a resampled RRT-Connect path.

This is an illustrative path-smoothing objective, not the complete CHOMP algorithm. The index represents a uniformly spaced path parameter; without a specified timing it does not establish actual joint accelerations or dynamic feasibility.

With a quadratic smoothness objective and only affine endpoint and joint-limit constraints, the simplified problem can be a quadratic program. Realistic collision constraints and Cartesian pose constraints through nonlinear forward kinematics are generally nonlinear and can be nonconvex. A local optimizer can fail or return an invalid result even when a feasible path exists. If collision avoidance is expressed only as a penalty, a lower objective value alone does not establish collision freedom.

Checking collision only at the optimized waypoints can miss a collision between them. Validate the connecting motions at a suitable resolution or with an appropriate continuous check. The result is a geometric path unless timing is also assigned. MIT's [motion-planning chapter](https://manipulation.mit.edu/trajectories.html) provides related examples and discusses local minima and discretized collision constraints.

### Cartesian targets, guesses, and requirements

Keep these roles distinct:

- A **Cartesian goal or task path** describes a desired end-effector pose or sequence of poses. It can become a hard constraint or a soft tracking cost.
- A **joint-space initial guess** is a starting point for a numerical optimizer; it does not have to be a required path.
- A **required waypoint** must be satisfied to the chosen tolerance; a **preferred waypoint** can instead be encouraged by a cost.

For example, a painting task may specify a desired end-effector path while allowing the optimizer to choose the corresponding arm configurations. The optional Bodily, Allen, and Killpack paper uses desired end-effector poses and jointly plans base position and joint motion; its core optimization is a quadratic program. Avoid implying that all nonlinear Cartesian tracking or collision problems are themselves quadratic programs.

## How the methods fit together

### RRT-Connect at a glance

For the reversible geometric planning examples in this unit:

1. Initialize one tree at the start configuration and one at the goal.
2. Sample a configuration and extend the active tree toward it using the chosen distance, interpolation, and collision checker.
3. Attempt to connect the other tree to the newly added configuration by extending toward it repeatedly until it reaches the configuration or is blocked.
4. If the trees connect, reconstruct the path from the two trees; otherwise, alternate which tree is active and repeat until the planning budget is exhausted.

Each extension must check the connecting motion, not just its endpoints. The arm example can use collision-checked interpolation in joint space; the basic 2D mobile example assumes a compatible geometric motion model.

### Sampling followed by optimization

For a start-to-goal arm motion in a cluttered scene, an instructional pipeline can be:

1. Define the robot configuration space, start and goal, joint limits, scene, and collision checker.
2. Use RRT-Connect to search for a feasible route.
3. Optionally resample that path and use it to initialize a trajectory optimizer.
4. Evaluate task satisfaction, collision validity, path quality, and computation time.
5. If the path will be executed, add appropriate timing and consider the robot's execution requirements.

The optimizer may start from a simple interpolation or another seed, and it may fail. A sampling planner can also fail within its allocated time. An optimized result must be validated rather than assumed valid or better.

MoveIt documents CHOMP initialization from an OMPL path in its [CHOMP guide](https://moveit.picknik.ai/main/doc/how_to_guides/chomp_planner/chomp_planner_tutorial.html). Check the chosen software version and configuration before relying on a particular integration or adapter. A supplied small numerical example is a suitable alternative if ROS/MoveIt setup would dominate the exercise.

For a task with a prescribed Cartesian path, the starting point is different: formulate tracking or pose requirements through forward kinematics, then choose joint motions that satisfy the task and relevant limits. A separate route planner may still be useful for approaching or leaving the task path.

## Suggested practical work and assessment

A connected two-part assignment would exercise both method families:

1. **Sampling-based planning:** implement RRT-Connect in a provided 2D framework. Use an idealized base, then apply the same planner interface to a supplied two-joint arm with an appropriate collision checker.
2. **Optimization:** use a supplied optimizer to refine an initial waypoint sequence. Modify or specify the objective and constraints, try more than one initial path, and validate the output.
3. **Comparison:** report feasibility, failures, planning time, and at least one path-quality measure. Explain the observed tradeoffs and recommend an approach for a particular task.

Provide the robot model, state-validity functions, visualization, optimizer interface, example scenes, and clear time budgets. Students can focus on the planner and optimization formulation instead of building a robotics software stack from scratch.

For a fair comparison, use the same task, scene, validity criteria, and stated computational budget. Report failures as well as successful runs, separate RRT planning time from optimization time when using a combined pipeline, and use clearly defined metrics. Multiple random seeds make it possible to discuss variability, though a small classroom sample supports only limited conclusions.

Credit a well-supported diagnosis when an optimizer or randomized planner fails; failure within a time budget does not prove that no feasible path exists.

## University and technical references

These sources informed the scope and provide materials for further adaptation. They include introductory robotics courses as well as dedicated planning courses; the list is illustrative rather than an exhaustive curriculum survey.

- **Cornell, Foundations of Robotics:** the undergraduate and graduate course versions place motion planning in weeks 10–11 and identify graph-based and sampling-based planning as learning outcomes. [Course syllabus](https://www.cs.cornell.edu/courses/cs5750/2021fa/syllabus/)
- **MIT, Robotic Manipulation:** notes and exercises covering configuration-space planning, RRT, RRT-Connect, shortcutting, inverse kinematics, and kinematic trajectory optimization. [Motion-planning chapter](https://manipulation.mit.edu/trajectories.html)
- **Iowa State, Motion Planning for Robotics and Autonomous Systems:** a dedicated course including configuration space, collision detection, randomized planning, differential constraints, and Python implementation. [Course description](https://www.cs.iastate.edu/courses/com-s-5760)
- **Johns Hopkins, Robot Motion Planning:** a mechanical engineering course covering configuration space, arm motion, graph search, representations, and nonholonomic constraints. [Spring 2025 syllabus](https://apps.ep.jhu.edu/syllabus/spring-2025/535.622.81)
- **Technical University of Munich, Robot Motion Planning:** a dedicated course progressing from configuration-space representations to roadmaps, PRM, and RRT. [Summer 2024 syllabus](https://mvp.in.tum.de/courses/motion/syllabus.html)
- **OMPL:** a library of sampling-based planners with tutorials on state validity, robot-arm planning, and benchmarking. [OMPL tutorials](https://ompl.kavrakilab.org/tutorials.html)
- **Optional BYU paper:** Bodily, Allen, and Killpack, “Motion planning for mobile robots using inverse kinematics branching” (2017). [BYU ScholarsArchive record](https://scholarsarchive.byu.edu/facpub/3204/)
- **Dynamic trajectory optimization:** an introductory direct-collocation tutorial. [Kelly, 2017](https://epubs.siam.org/doi/10.1137/16M1062569)
- **Learning outcomes:** [BYU outcome-writing guidance](https://learningoutcomes.byu.edu/files/Write_Effective_Course_Outcomes.pdf) and an [engineering education guide on aligning outcomes and assessment](https://eer.engin.umich.edu/wp-content/uploads/sites/670/2024/05/Svinicki-Conceptual-Frameworks.pdf).
