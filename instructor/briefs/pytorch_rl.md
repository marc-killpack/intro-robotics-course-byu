# PyTorch and reinforcement learning: course design

## Purpose and status

This working brief is for an introductory robotics course in the BYU mechanical engineering department. It is intended for the separate Codex session working on the course repository, alongside the path-planning and computer-vision/visual-servoing briefs.

The proposed core is **two weeks, with six 50-minute lectures**:

- **Week 10:** introductory supervised learning and PyTorch, with a guided image-classification exercise related to the conveyor.
- **Week 11:** introductory reinforcement learning (RL), with a provided environment and Stable-Baselines3 (SB3).
- **Optional during the three project weeks:** one 50-minute lecture, or up to three lectures, on learned robot locomotion, demonstrations, and vision-language-action (VLA) models. These optional sessions have **no additional homework**; their class time comes from the existing project period.

The specific lecture plans, assignments, and software choices are proposals, not final syllabus decisions. The instructor is especially interested in students' capabilities and judgment, not only terminology.

**Imitating visual servoing and improving the learned policy are optional final-project extensions, not required exercises in weeks 10–11.** The core RL activity remains a short, guided demonstration or exercise using a provided environment or checkpoint. If infrastructure and time permit, a project team may use visual-servoing demonstrations to train a policy, compare it with the original controller, and optionally investigate whether further training makes it faster. No team must pursue these extensions to complete the project.

### Guidance for the receiving Codex session

- Inspect the actual course repository, its instructions and conventions, existing simulation, Python stack, and Docker configuration before proposing implementation.
- The instructor wants changes to student repositories tracked and approved rather than made implicitly. Determine whether the repository is a student repository; if unclear, ask what the code is for. Prepare concrete, reviewable changes and follow applicable approval instructions.
- Reuse existing robot, camera, visualization, and notebook interfaces where practical. Do not assume a particular simulator, ROS version, Python version, GPU, or display setup.
- This conversation is a standalone handoff. **No course code or Docker image has been inspected, modified, or tested here.**

## Starting point and intended connection

Students have seen basic programming, robot kinematics and Jacobians, camera geometry, planar calibration, OpenCV segmentation and tracking, elementary visual servoing, and the idea of an optimization objective. They do not need an advanced machine-learning or optimization course.

A possible conveyor pipeline is:

```text
camera image -> OpenCV object segmentation/crop -> learned class label
             -> centroid/tracking + planar calibration -> position/velocity
             -> task logic and visual-feedback controller -> robot motion
```

**Segmentation locates object pixels; classification assigns a category.** Position and velocity are separate measurements produced by the vision and tracking pipeline. A class label is not a robot action or a complete control policy. Neural-network segmentation can be mentioned, but is not part of the core exercise.

The RL week introduces a learned mapping from observations to actions. A simulated planar robot exercise would connect especially well to the preceding unit, but it is feasible only if a suitable environment and baseline already exist or are prepared and piloted. Otherwise, use a lightweight provided control example such as Gymnasium's `CartPole-v1` and discuss robot reaching conceptually.

## Recommended priorities

| Priority | Topic or capability | Scope |
| --- | --- | --- |
| Essential | Labeled data, generalization, and leakage | Training, validation, test, overfitting, and independent evaluation cases. |
| Essential | PyTorch workflow | Tensors, a small provided model, predictions, loss, autograd, and optimizer updates. |
| Essential | Conveyor classification | Classify extracted object crops; compare with a simple color or shape rule; inspect mistakes. |
| Essential | RL and feedback | Observation, action, reward, episode, policy, return, and the environment interaction loop. |
| Essential | Running and evaluating a provided policy | Use SB3 and a prepared environment or checkpoint; interpret task success and failures. |
| Essential | Engineering judgment | Compare learning and classical control based on task, observations, data, computation, constraints, and evidence. |
| Useful if time permits | PPO intuition | Explain rollouts, policy/value estimates, and controlled policy updates without deriving or implementing PPO. |
| Optional project extension | Imitation of visual servoing | Train a small policy on logged observation–action pairs; compare with the baseline on held-out scenes. |
| Optional final-project stretch goal | Improve the policy in simulation | Teams may investigate speed during the project using a suitable objective and fresh simulated experience; this is not a required weekly exercise, and improvement is not guaranteed. |
| Optional project-period lectures | Locomotion, demonstrations, and VLAs | Use prepared videos and small data examples; no full-scale model training or homework. |
| Outside core | Full neural segmentation, custom physics, PPO derivation, and humanoid training | Mention as future work, not as prerequisites. |

PPO is a reasonable **teaching recommendation**, not a claim that it is the best or industry-standard algorithm for every problem. SB3 uses PyTorch, but a student can use SB3 without implementing its network training. Neural networks are common policy representations, although an RL policy need not be a neural network.

## Proposed learning outcomes

By the end of the core two-week unit, students should be able to:

| ID | Outcome | Possible evidence |
| --- | --- | --- |
| ML1 | **Distinguish** segmentation, classification, and feedback control in a conveyor pipeline. | Identify each stage's inputs and outputs and explain the effect of a labeling versus localization error. |
| ML2 | **Prepare and interpret** labeled examples and leakage-resistant training, validation, and test splits. | Inspect crops and labels; group related frames or scenes; explain what a held-out test measures. |
| ML3 | **Trace** a PyTorch learning update through prediction, loss, gradients, and parameter changes. | Annotate and modify a provided training loop and identify its input and output shapes. |
| ML4 | **Train and use** a provided small image classifier. | Run a guided exercise, save or reload a model, and label a new crop using the same preprocessing. |
| ML5 | **Evaluate** a classifier and explain its limitations. | Report held-out accuracy and class-wise errors, inspect examples, and compare a simple baseline. |
| RL1 | **Specify** an RL problem using observations, actions, rewards, episode endings, and desired behavior. | Annotate a control diagram or explain these elements in a provided environment. |
| RL2 | **Explain** how a policy provides feedback and how RL differs from supervised classification. | Trace observation to action to response; distinguish reward feedback from an action label. |
| RL3 | **Run and inspect** a provided SB3 policy experiment. | Run or load a policy, evaluate separate episodes, and identify the PyTorch policy components conceptually. |
| RL4 | **Evaluate and compare** control approaches using task-relevant evidence. | Report success and failure on multiple cases and discuss variability, observations, and limitations. |
| RL5 | **Justify** whether a learned policy is plausible for a stated robot task. | Compare data, simulation, training effort, model assumptions, and potential failures with a classical controller. |

If a runnable RL exercise cannot be prepared and piloted, adjust RL3 to ask students to interpret a provided recording and results instead. These are unit-level outcomes, not claims of program-level attainment. They emphasize observable abilities and evidence, consistent with [BYU's course-outcome guidance](https://learningoutcomes.byu.edu/files/Write_Effective_Course_Outcomes.pdf).

**Optional extension outcomes:** students could learn to distinguish imitation learning from RL and a VLA model from a training algorithm; interpret a demonstration or motion-reference dataset; explain the role of simulation and real-world validation; and compare a cloned policy with its visual-servoing baseline.

## Six-lecture outline

Each proposed session totals 50 minutes. Prepare demonstrations and sample results in advance. Small worked examples and prediction questions should take priority over surveying many architectures.

| Lecture | Proposed sequence | Capability emphasized |
| --- | --- | --- |
| **10.1: Supervised perception** | **10 min:** conveyor pipeline and segmentation versus classification. **15 min:** labeled examples and input/target. **15 min:** splits, overfitting, and leakage. **10 min:** inspect crops and predict mistakes. | Identify a useful task and design a meaningful evaluation. |
| **10.2: A PyTorch training step** | **10 min:** tensors and image preprocessing. **15 min:** a provided model, scores, and loss. **15 min:** autograd and optimizer updates. **10 min:** trace a batch and check shapes. | Explain and use the basic training calculation. |
| **10.3: Train and evaluate** | **15 min:** guided training or prepared checkpoint. **15 min:** held-out accuracy and errors. **10 min:** compare a simple rule. **10 min:** use a label in the conveyor pipeline. | Evaluate a classifier as part of a robot system. |
| **11.1: RL as feedback** | **10 min:** control example and goal. **15 min:** observation, action, environment, episode. **15 min:** reward, return, exploration, and episode endings. **10 min:** map concepts to a robot or provided environment. | Formulate an RL control problem. |
| **11.2: Policies and SB3** | **15 min:** policy and value-function intuition. **10 min:** PPO concept. **15 min:** run or inspect an SB3 experiment. **10 min:** inspect the PyTorch policy and connect it to week 10. | Understand what is learned and use a prepared tool. |
| **11.3: Evaluate and choose** | **15 min:** evaluate a trained or supplied agent. **15 min:** baseline and failures; compare a planar controller if ready. **10 min:** seeds and simulation-to-real gap. **10 min:** project possibilities. | Interpret evidence and decide when RL is worth investigating. |

The optional project-period material is additional to these six sessions. If time is tight, prioritize data splits and evaluation over additional network architectures, and the RL feedback loop over mathematical derivations.

## Week 10: supervised learning and PyTorch

### The basic idea

An example consists of an object crop \(x_i\) and a label \(y_i\), such as circle, triangle, or rectangle. A model \(f_\theta\) produces class scores, and training adjusts parameters to reduce average training loss:

\[
\min_\theta \frac{1}{N}\sum_{i=1}^{N} L\bigl(f_\theta(x_i),y_i\bigr).
\]

This connects to the previous optimization unit; students do not need to implement an optimizer. Training loss is not a measure of performance on genuinely new scenes. Validation data informs development choices; reserve test data for final evaluation.

A guided mini-batch update can expose the essential operations:

```python
# The instructor supplies model, loss_fn, optimizer, and a batch.
model.train()
logits = model(images)             # class scores for each image
loss = loss_fn(logits, labels)     # CrossEntropyLoss; integer class indices
optimizer.zero_grad()
loss.backward()                    # autograd computes gradients
optimizer.step()                   # optimizer updates the parameters
```

Use `model.eval()` and `torch.inference_mode()` at evaluation, with the same preprocessing and label mapping. Standard PyTorch `CrossEntropyLoss` expects unnormalized logits; do not add a softmax before that loss. See the [PyTorch quickstart](https://docs.pytorch.org/tutorials/beginner/basics/quickstart_tutorial.html) and [optimization tutorial](https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html).

### Guided assignment: classify conveyor objects

1. Supply a small labeled set of synthetic or recorded scenes and crops, data loading, plotting, and a small network scaffold. Inspect images and labels before training.
2. Split by independent original object, scene, or recording sequence as appropriate. Do not distribute nearly identical adjacent frames randomly among training, validation, and test. Preserve class coverage and document the grouping.
3. Inspect tensor dimensions and preprocessing. OpenCV often supplies BGR images in height × width × channels; a PyTorch model commonly expects RGB in batch × channels × height × width. Check the actual model's convention, data type, and scaling.
4. Trace or complete the training calculation, run a piloted CPU-sized training example, and examine training and validation results.
5. Report held-out accuracy and a confusion matrix or class-wise errors. Show examples of correct and incorrect predictions and discuss what might cause mistakes.
6. Compare with a provided simple rule, such as a contour-geometry rule for shape or a color threshold, on the same eligible test crops. Discuss when the simpler method is enough.
7. Apply the saved classifier to crops from a prepared conveyor frame or short sequence. Explain what happens when segmentation misses an object or produces a poor crop.

Avoid a dataset in which each shape always has its own color or background: a model may learn that shortcut instead of the intended shape. Vary appearance, rotation, position, background, and crop quality as appropriate. Performance on synthetic images alone does not establish performance on a physical camera.

A small supplied convolutional network is a reasonable default. A frozen pretrained feature extractor with a trainable final layer is an alternative if compatible weights, licensing, storage, and CPU runtime are already handled; see [PyTorch's transfer-learning tutorial](https://docs.pytorch.org/tutorials/beginner/transfer_learning_tutorial.html). Neither a GPU nor a pretrained backbone should be required without a successful pilot.

Provide a trained checkpoint and sample results as a fallback. Grade the workflow, evaluation, and honest explanation of errors rather than requiring a particular accuracy.

## Week 11: reinforcement learning

### Connect RL to feedback control

A feedback controller repeatedly measures a system and selects a command. A learned RL policy also responds to observations, but its parameters are trained from interaction experience and a reward signal.

| Element | Planar reaching example | Meaning |
| --- | --- | --- |
| Observation \(o_t\) | Measured target and end-effector position or error, possibly velocity | What is available to the policy; it may be noisy or omit part of the true state. |
| Action \(a_t\) | A bounded planar velocity or joint command | What the policy asks the system to do, with explicit units and limits. |
| Environment | A provided plant and target | Responds to actions and produces the next observation. |
| Reward \(r_t\) | A signal encouraging target acquisition | Feedback for training, not a per-step correct-action label. |
| Episode ending | Target reached, failure, or timeout | Defines a trial; distinguish task termination from a time limit. |
| Policy \(\pi_\theta(a\mid o)\) | A network or rule maps measurements to commands or an action distribution | The behavior executed in closed loop. |

For an episodic task, one common goal is:

\[
\max_\theta \mathbb{E}_{\pi_\theta}[G_0],
\qquad
G_0=\sum_{t=0}^{T-1}\gamma^t r_t.
\]

Here \(\gamma\) is a discount factor, often between 0 and 1. The reward is a designer's proxy for the task; higher return alone does not prove the robot accomplished the intended task. Report independent success and error metrics as well.

A proportional or Jacobian-based visual controller also maps measured errors to commands. Its law is designed using geometry and control; an RL policy's parameters are learned from experience. Both depend on measurements, timing, action limits, and task definitions. The true simulator state may be cleaner than a camera-derived measurement. If a target moves, include measured velocity or a suitable history when needed rather than assuming one image contains target velocity.

### SB3 and PPO at an introductory level

With a provided [SB3 PPO](https://stable-baselines3.readthedocs.io/en/master/modules/ppo.html) example:

1. The current policy interacts with the environment, collecting observations, actions, and rewards.
2. PPO uses these trajectories and a value estimate to update the policy; its clipping mechanism is intended to limit excessively large changes.
3. The process repeats; the resulting policy is evaluated on separate episodes. PPO does not require differentiating through the simulator.

In this example, a PyTorch network represents the actor. SB3's `model.policy` is a PyTorch module that also contains value-function components; students can inspect it without understanding every layer. `MlpPolicy` is for vector observations, not raw camera images. PPO can support both continuous and discrete action spaces with suitable environments.

Students need not implement PPO, derive its objective, build a custom environment, or write the policy network from scratch. SB3 supplies RL-specific rollout collection and learning; PyTorch handles network parameters and gradients.

Gymnasium's ordinary `reset()` returns `(observation, info)` and `step()` returns `(observation, reward, terminated, truncated, info)`. SB3's vectorized environment API differs; consult [Gymnasium basic usage](https://gymnasium.farama.org/introduction/basic_usage/) and [SB3 vectorized environments](https://stable-baselines3.readthedocs.io/en/master/guide/vec_envs.html).

### Guided RL exercise

The default is an **in-class notebook or demonstration** with a prepared environment, initialized policy, trained checkpoint, and evaluation code. A short optional take-home reflection is possible if workload permits. Learning from visual-servoing data and training for greater speed are optional final-project extensions, not requirements of this exercise.

- Identify the observations, actions, reward, and episode endings. Run or inspect a brief training process and examine the PyTorch policy module.
- Evaluate an untrained or simple baseline and a trained or supplied policy on the same independent evaluation cases. Report return and a meaningful task metric such as success rate, time to target, or final error.
- Inspect successes and failures where available. Record the training budget and seeds or case selection. Multiple evaluation episodes matter; multiple training seeds are valuable if feasible.
- Provide a checkpoint, plots, and video if live training is slow or unreliable. Do not grade on a particular RL score or require that a learned policy beats the baseline.

**Environment preference:** use a provided and piloted planar reaching environment if available; otherwise use a lightweight control environment such as `CartPole-v1`, plus a conceptual robot-reaching example. CartPole is not a conveyor robot or visual-servo comparison. If neither runs dependably, analyze prepared recordings and results, adjusting the outcome accordingly.

## Optional final-project extension: learn from visual servoing

### Is it reasonable?

**Yes, as a staged optional final-project extension if the course supplies a working simulated visual-servo controller and the logging/training scaffold.** A team may choose to demonstrate the controller, imitate it, and compare the results. Investigating whether further RL training can improve speed is an additional, more uncertain project stretch goal. None of these stages is a required weekly exercise or a dependency for completing the conveyor project.

| Stage | Student activity | Feasibility and interpretation |
| --- | --- | --- |
| **1. Demonstrate the expert** | Run a working visual-servo controller and collect many episodes. | Start with a fixed target and a simple planar task; a moving target adds estimation and interception difficulty. |
| **2. Clone the policy** | Use logged measurements and controller commands as supervised observation–action pairs; train a small network and run it in the same simulator. | This is behavioral cloning or imitation learning, not RL. It is most reasonable if data collection, a model, and evaluation code are supplied. |
| **3. Compare** | Evaluate the cloned policy and the original controller on held-out cases. | Focus on success, error, time, and failures. A clone is trained to reproduce its teacher, so it should not be expected to be faster. |
| **4. Optional project stretch: improve speed** | A team may continue training against a task objective in simulation, for example with PPO, and compare again. | This is optional project work, not a required exercise. It needs a compatible environment, testing, and fresh interaction; improvement is not guaranteed. |

Even a failed cloning attempt is educational if students can diagnose why it fails. Matching action labels on recorded frames is easier than controlling the robot when the clone's own mistakes lead it to unfamiliar states. More diverse demonstrations and, as a further extension, collecting expert labels on states visited by the clone can help; see [the imitation library's behavioral-cloning overview](https://imitation.readthedocs.io/en/stable/algorithms/bc.html) and its [DAgger description](https://imitation.readthedocs.io/en/stable/algorithms/dagger.html). Neither method is required in the core unit.

### What the demonstrations must contain

Provide timestamped episodes, not just videos. At each controller step, log:

- The **same observations** the policy will receive later: for example, camera-derived planar target and end-effector position or error, robot joint state when needed, and a target-velocity estimate or history for a moving object.
- The expert's issued action, in the same coordinates and units intended for the clone: for example, bounded joint-velocity commands. Record the controller period, command limits, target identity, termination, and relevant failures.
- Enough metadata to reconstruct preprocessing, frame conventions, normalization, time alignment, and missing/noisy measurements. Do not silently give the learned policy perfect simulator state while calling it a camera-based comparison.
- Varied initial configurations and target positions; for a moving conveyor, include the relevant target speeds and directions. Split training, validation, and test by complete episodes or scenarios.

The first version can use the low-dimensional visual measurements already produced by OpenCV and the planar homography. Learning directly from raw images would add network and data complexity and is a separate stretch. If actions are joint commands, provide enough robot configuration information for the policy to handle different poses; a two-dimensional image error alone need not uniquely determine the right joint command.

A small PyTorch regression model trained with observation–action pairs is sufficient to illustrate cloning. Alternatively, the [imitation library](https://imitation.readthedocs.io/en/stable/tutorials/1_train_bc.html) offers an SB3-compatible behavioral-cloning workflow, subject to checking package compatibility. Prepare and test data conversion and rollout code; do not assume the library will accept the course's logs without adaptation.

### Optional project stretch: investigate a faster policy

Teams that choose this stretch goal can investigate whether further simulation training improves task speed. A speed improvement is an optimization goal, not something ordinary cloning guarantees. First compare against a **sensibly tuned classical baseline**, including an appropriate safe gain and the same velocity limits. Otherwise, a learned policy may appear better simply because the baseline was unnecessarily slow.

For a simulation-only stretch, formulate a task that rewards completing the interception quickly while penalizing missed objects, excessive commands, collisions or limit violations as appropriate. Check that the actual success criterion matters more than exploiting the reward. Time-to-intercept and successful pickup can differ: a fast approach that misses the object is not a successful improvement.

PPO is an on-policy algorithm: further training requires **new environment interactions**, not only the fixed demonstration log. Initializing its actor from a cloned model is an extra integration step. A plain PyTorch regression model is not automatically an SB3 PPO actor: observation/action spaces, preprocessing, network architecture, action distribution, and policy parameters must be compatible, and PPO also maintains a value network. The course team must implement and test the bridge or supply a compatible checkpoint; students should not be expected to solve this integration independently. If no bridge exists, train a separate PPO policy as an exploratory comparison rather than calling it a fine-tuned clone.

### Fair comparison and success criteria

- Use the same task, simulation, controller period, action bounds, and held-out initial scenes for the classical controller, cloned policy, and any RL policy. Supply the same camera-derived measurements and noise unless a sensing difference is explicitly part of the study.
- Report **success rate and failures**, error, time to completion or interception, constraint violations, and commands or smoothness as appropriate. Report time together with the number of failures; timing only successful trials can hide a risky policy.
- Record how much data, training, and tuning each method required. Use multiple evaluation episodes and, when feasible, multiple training seeds.
- Evaluate fixed and moving targets separately. Moving targets, lost detections, camera noise, and imperfect calibration are harder extensions. Do not claim simulated success automatically transfers to hardware.
- Use a prepared classical baseline and a trained-clone checkpoint so that comparison remains possible if training fails. Hardware deployment is not required.

## Optional project-period lectures: locomotion, demonstrations, and VLAs

One lecture can provide an overview; three lectures can go further. Both options use existing project-period class time and assign **no additional homework**.

### Important distinctions

| Approach | Core idea | Relationship to the others |
| --- | --- | --- |
| RL locomotion/control | Learn a policy using experience and reward, often with many simulated trials; test in simulation and on the robot. | Human motion references, other learned components, and conventional low-level control may all contribute. |
| Imitation / behavioral cloning | Use demonstration observation–action pairs as supervised training examples. | Demonstrations can also guide RL. Imitation and RL are different methods that can be combined. |
| VLA model | Use vision and language information to predict robot actions; particular models may also use robot state or history. | VLA describes a model role and interface, not a single mandatory training method. |
| Classical robotics and control | Use geometry, planning, state estimation, optimization, and feedback. | Can provide baselines, constraints, lower-level controllers, demonstration data, and complementary modules. |

RL is prominent in many recent humanoid and quadruped locomotion systems, but it is not the sole technique used in robot locomotion. A VLA is not synonymous with an RL-trained policy. Ask: What is observed? What is commanded? Where did the learning signal come from? What conditions were actually tested?

### Verified examples and discussion prompts

These sources describe particular research or company demonstrations; do not assume all versions of a commercial robot use the same controller.

- **Quadruped:** ETH Zurich's [ANYmal locomotion work](https://rsl.ethz.ch/the-lab/news/2020/10/learning-locomotion-over-challenging-terrain.html) applies deep RL to locomotion on varied terrain. Discuss contact, onboard sensing, disturbances, and transfer.
- **Humanoid walking:** [Figure's walking demonstration](https://www.figure.ai/news/reinforcement-learning-walking) describes an RL walking controller trained in simulation. Discuss practice, feedback, and real-robot transfer.
- **Whole-body humanoid behavior:** Boston Dynamics describes [Atlas lifting a refrigerator](https://bostondynamics.com/blog/training-a-humanoid-robot-for-hard-work) using RL, a motion reference, and simulated variations. This combines manipulation and balance.
- **Digit and hybrid control:** Castillo and colleagues' [Digit paper](https://cyberboticslab.com/publication/castillo-2021-robust/castillo-2021-robust.pdf) combines an RL motion policy with feedback regulation and reports physical-robot testing. It is a research result, not a claim about every production Digit behavior.
- **Combined methods:** Figure reports that [Helix 02](https://www.figure.ai/news/helix-02) uses human motion data and sim-to-real RL in its whole-body controller. It illustrates that demonstrations and RL can appear in one system.
- **VLA and demonstration data:** Google DeepMind's [RT-2](https://deepmind.google/blog/rt-2-new-model-translates-vision-and-language-into-action/) connects vision and language to robot manipulation using robot demonstrations. It is not a humanoid locomotion example or evidence that every VLA is trained with RL.
- **Academic whole-body example:** [HOVER](https://hover-versatile-humanoid.github.io/) provides a learned humanoid-controller paper and videos. Discuss policy outputs and the role of lower-level control.

### One-lecture option

| Time | Activity |
| --- | --- |
| 10 min | Show one quadruped and one humanoid example; identify observations, actions, and real versus simulated parts. |
| 10 min | Explain demonstration data and behavioral cloning; contrast action labels with rewards. |
| 15 min | Inspect the visual-servoing imitation example or prepared data; predict what happens on an unfamiliar state. |
| 10 min | Show a VLA example; distinguish its interface from its training data and algorithms. |
| 5 min | Discuss one limitation and a possible role for classical robotics. |

### Three-lecture option

| Session | Sequence | Main capability |
| --- | --- | --- |
| **A: Learned locomotion** | **10 min:** observations and actions. **15 min:** simulated reward-based practice and variation. **15 min:** robot example. **10 min:** feedback and transfer discussion. | Interpret an RL locomotion system. |
| **B: Learning from examples** | **10 min:** demonstrations and motion references. **15 min:** behavioral cloning. **15 min:** inspect the planar servo imitation demo. **10 min:** unfamiliar states and feedback errors. | Connect supervised training to a learned controller. |
| **C: VLA and integration** | **15 min:** image, language, state, and action. **15 min:** example system or dataset. **10 min:** VLA, RL, and classical control. **10 min:** project discussion. | Explain how model components and training methods fit together. |

### Prepared data and teaching tools

- [Open X-Embodiment](https://github.com/google-deepmind/open_x_embodiment) collects examples from many robots and provides visualization tools. Prepare a short preview and inspect available images, actions, and language or state; formats, units, and licenses vary. Many datasets concern robot arms rather than humanoids.
- [HOLD human motion data](https://github.com/rai-opensource/hold) can illustrate motion references with a short prepared clip or plot. Motion capture is not automatically an image–language–action demonstration.
- Use notebooks, plots, short videos, and a prepared imitation dataset. Students need not download full datasets, install large humanoid simulators, or train a VLA. Check the terms for any redistributed material.

## Assessment and workload

- **Supervised assignment:** inspect data and splits, complete or trace a guided training loop, test the model, and compare a rule-based baseline. Supply most infrastructure.
- **RL core:** a short in-class exercise or reflection. If assigned outside class, bound the workload and provide a trained fallback. It does not require collecting visual-servo demonstrations, cloning a policy, or training one for speed.
- **Optional project-period lectures:** no additional homework; use discussion or ungraded in-class predictions.
- **Final project:** classification may label conveyor objects. If infrastructure and time support it, teams may choose the optional imitation and comparison extension, with faster-policy training as a further optional project stretch. These are not required weekly exercises or required for project completion. Assess a chosen extension on its evidence and interpretation, not on achieving a speed improvement.

A well-explained failed or underperforming model can demonstrate meaningful learning. Pilot actual workloads before setting time, memory, or performance expectations.

## Software and data requirements for the receiving repository

The following are recommendations, not verified facts about the existing environment:

- Select compatible versions of PyTorch, SB3, and Gymnasium for the actual Python and operating system. Add `torchvision` only if needed and match it to PyTorch. Treat the `imitation` library as optional and check its dependency compatibility before adding it.
- Reuse existing NumPy, OpenCV, plotting, notebook, and simulation interfaces. A headless OpenCV package may suit a headless container, but check existing dependencies and avoid conflicting OpenCV installations.
- Prefer a CPU-capable workflow and the existing compatible PyTorch build; do not assume a GPU, CUDA, internet access, or an assignment-time download. Pin or record resolved versions according to repository conventions after testing.
- Provide labeled crops, independent split identifiers, class names, generation settings, model scaffold, checkpoint, and sample results. Document data provenance, preprocessing, and redistribution terms.
- Provide a selected RL environment, checkpoint, evaluation notebook, and video/plot fallback. For imitation, provide timestamped demonstration logs, a known-good servo baseline, conversion code, and a trained clone if that extension is pursued.
- Optional humanoid/VLA examples should use short prepared media and data previews; large models, full datasets, and specialized humanoid training simulators need not enter the student image.

### Suggested checks in the target environment

1. Build and start the existing image without breaking the previous robotics, vision, or servo exercises.
2. Import the selected packages and run a small PyTorch forward/backward/update on CPU.
3. Convert an OpenCV crop to the classifier's expected layout and dtype, then save, reload, and evaluate a supplied model.
4. Reset and step the chosen Gymnasium environment, load an SB3 policy, and run separate evaluation episodes; check time-limit handling and headless output if used.
5. If the optional project extension is offered and supported, collect a servo demonstration, train or load a clone, and evaluate it under the same conditions as the baseline. Test the SB3 initialization bridge separately before offering RL fine-tuning as a project stretch goal.
6. Pilot runtime and memory on representative student hardware, verify offline operation and data terms, and supply fallback results.

These checks must be performed in the target repository; they **have not been run here**.

## Reading and references

### Core resources

- [PyTorch quickstart](https://docs.pytorch.org/tutorials/beginner/basics/quickstart_tutorial.html) and [optimization tutorial](https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html) — models, training, evaluation, and updates.
- [PyTorch transfer learning](https://docs.pytorch.org/tutorials/beginner/transfer_learning_tutorial.html) — optional pretrained-feature alternative.
- [Gymnasium basic usage](https://gymnasium.farama.org/introduction/basic_usage/) — environment interaction and episode endings.
- [Stable-Baselines3 PPO](https://stable-baselines3.readthedocs.io/en/master/modules/ppo.html), [custom policies](https://stable-baselines3.readthedocs.io/en/master/guide/custom_policy.html), and [RL tips](https://stable-baselines3.readthedocs.io/en/master/guide/rl_tips.html) — policy use and evaluation.
- [OpenAI Spinning Up: introduction to RL](https://spinningup.openai.com/en/latest/spinningup/rl_intro.html) — introductory RL concepts.
- [BYU: Make Learning Outcomes Work for You](https://learningoutcomes.byu.edu/files/Write_Effective_Course_Outcomes.pdf) — outcome-writing guidance.

### Optional extensions

- [Behavioral cloning tutorial](https://imitation.readthedocs.io/en/stable/tutorials/1_train_bc.html) and [DAgger overview](https://imitation.readthedocs.io/en/stable/algorithms/dagger.html) — learning policies from demonstration data.
- [ANYmal locomotion](https://rsl.ethz.ch/the-lab/news/2020/10/learning-locomotion-over-challenging-terrain.html), [Digit RL and feedback paper](https://cyberboticslab.com/publication/castillo-2021-robust/castillo-2021-robust.pdf), and [HOVER](https://hover-versatile-humanoid.github.io/) — university research examples.
- [Figure RL walking](https://www.figure.ai/news/reinforcement-learning-walking), [Figure Helix 02](https://www.figure.ai/news/helix-02), and [Boston Dynamics Atlas training](https://bostondynamics.com/blog/training-a-humanoid-robot-for-hard-work) — company descriptions and videos.
- [Google DeepMind RT-2](https://deepmind.google/blog/rt-2-new-model-translates-vision-and-language-into-action/) and [OpenVLA](https://openvla.github.io/) — VLA manipulation examples.
- [Open X-Embodiment](https://github.com/google-deepmind/open_x_embodiment) and [HOLD](https://github.com/rai-opensource/hold) — different types of robot and motion data.
- [Berkeley Deep RL course](https://rail.eecs.berkeley.edu/deeprlcourse/) — an advanced follow-on resource, not a core prerequisite.
