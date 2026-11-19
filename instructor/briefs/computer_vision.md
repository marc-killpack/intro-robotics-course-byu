# Computer vision and visual servoing: two-week course design

## Purpose and status

This is a working brief for an introductory robotics course in the Brigham Young University mechanical engineering department. It is intended to be handed to a Codex session working on the course repository.

The provisional unit is **two weeks, with six 50-minute lectures**:

- **Week 8:** introductory computer vision with OpenCV, including camera geometry, a planar homography, segmentation, object features, tracking, and planar velocity.
- **Week 9:** visual servoing, beginning with a fixed camera and planar robot motion and progressing toward a camera mounted near the arm's tool.

The camera can be oblique and positioned in 3D; the relevant final-project workspace and motion are planar. Students already know homogeneous transforms and robot kinematic Jacobians. They should use that background to connect camera measurements to robot motion.

**Neural-network training is a separate part of the course.** Classification can be mentioned as a source of labels, but training a classifier is not an outcome or required activity for these two weeks. Stereo is an optional extension.

The lecture plan, outcomes, assignments, and software implementation choices below are proposals to adapt with the instructor. They are not finalized syllabus requirements.

### Guidance for the receiving Codex session

- Inspect the actual course repository, course conventions, existing software stack, Docker configuration, and applicable instructions before proposing changes.
- The instructor wants changes to student repositories tracked and approved rather than made implicitly. Determine whether the repository is a student repository; if that is unclear, ask what the code is for. Prepare concrete, reviewable changes and follow applicable approval instructions.
- Reuse the existing simulator, exercises, language, notebooks, and dependency-management approach where practical. Do not assume a particular ROS distribution, simulator, Python version, Docker base image, or display system.
- Focus on student capabilities and observable evidence of learning as well as conceptual explanations.

### Environment status

This conversation is a standalone handoff for a different repository that contains the Docker files and course environment. The Docker image, package versions, available simulation tools, and compatibility with OpenCV **have not been verified here**. The environment section below provides requirements and checks for the receiving session.

## Scope and assumptions

Students are expected to have seen forward kinematics, homogeneous transforms, basic robot Jacobians, and elementary programming. Provide the robot model, visualization, camera or image generator, image-coordinate conventions, and baseline controller interfaces so that students can focus on the vision and control concepts.

The initial workspace is a known plane, such as a tabletop or conveyor. A fixed camera views that plane at an angle. Use objects or visible markers whose measured points lie on the calibrated plane, or at a known consistent height. The two-week unit does not require general 3D object reconstruction, full six-degree-of-freedom pose estimation, stereo reconstruction, or a physical robot.

A geometric path on the plane and a timed robot trajectory are different. Likewise, a pixel location, a physical point on the workspace plane, and a robot-base coordinate are different quantities. The exercises should make the coordinate frames, units, and assumptions explicit.

## Proposed core learning outcomes

By the end of the unit, students should be able to:

| ID | Proposed outcome | Possible evidence |
| --- | --- | --- |
| CV1 | **Project** a 3D point in camera coordinates into an image using a pinhole model, and interpret the roles of camera parameters and depth. | Calculate a pixel location for a given point; explain why one pixel does not specify a unique 3D point. |
| CV2 | **Calibrate** the mapping between an oblique camera image and a known planar workspace using corresponding points. | Estimate an image-to-plane homography and validate it against an additional point or measured distance not used in the fit. |
| CV3 | **Extract** useful object measurements from an image using OpenCV. | Segment a contrasting object and calculate its centroid, area, bounding box, and a simple orientation when its visible shape supports one. |
| CV4 | **Track** an object or visual feature across frames and estimate its planar position and velocity. | Use timestamps and a planar calibration to report position and velocity in physical units for a simulated conveyor object. |
| CV5 | **Evaluate** the accuracy and limitations of a vision pipeline using known or measured reference data. | Compare estimates with ground truth and explain an error caused by occlusion, lighting, camera distortion, tracking loss, or an incorrect plane assumption. |
| VS1 | **Formulate** a planar visual-servoing task using measured features, desired features, and a robot Jacobian. | Define the feature error and predict a corrective joint motion for a simple arm and stationary target. |
| VS2 | **Implement and evaluate** a simple planar visual-feedback controller using a provided robot model and vision interface. | Plot feature error over time, assess the task result, and describe how the controller handles a lost target. |
| VS3 | **Compare** fixed-camera and eye-in-hand configurations for a visual-servoing task. | Explain how camera motion changes image measurements, how the camera-to-tool relationship matters, and why a fixed-camera homography cannot simply be reused as the wrist camera moves. |

If no supported programming exercise is available, revise the implementation outcome to require use and interpretation of a provided controller. A well-diagnosed detection or control failure is valid evidence of learning; students should not be promised that every configuration or noisy measurement will converge.

### Optional outcomes

- **Track** point features with a provided Lucas–Kanade implementation and compare point tracking with re-detecting a segmented object's centroid.
- **Calibrate** camera intrinsics from checkerboard images rather than using provided parameters.
- **Interpret** an image Jacobian for an eye-in-hand camera, including the role of depth and the camera-to-tool transform.
- **Explain** why one centroid supplies only two image coordinates and cannot by itself specify a general six-degree-of-freedom pose.
- **Compare** image-based and position-based visual servoing for a given task.
- **Extend** a controller to a moving target using an estimated target velocity.

The outcomes are unit-level proposals. They can contribute evidence toward broader engineering program outcomes, but they do not by themselves establish attainment of program-level ABET outcomes. BYU's [outcome-writing guidance](https://learningoutcomes.byu.edu/files/Write_Effective_Course_Outcomes.pdf) emphasizes student abilities and evidence of learning.

## Six-lecture outline

Each proposed session totals 50 minutes. Practical work assumes a prepared image dataset or generator and software environment.

| Lecture | Proposed sequence | Capability emphasized |
| --- | --- | --- |
| **8.1: Camera geometry** | **10 min:** images, pixels, and coordinate conventions. **15 min:** pinhole projection and depth ambiguity. **15 min:** intrinsics, camera/world frames, and distortion. **10 min:** introduce the workspace-plane mapping. | Relate 3D geometry to an image and explain the assumptions used for a planar task. |
| **8.2: Homography and object features** | **20 min:** estimate and validate a planar homography. **20 min:** segmentation, contours, centroids, and shape. **10 min:** demonstration or exercise on an oblique image. | Map an oblique view to the workspace plane and extract usable image measurements. |
| **8.3: Tracking and velocity** | **10 min:** segmentation robustness. **10 min:** associate or track features across frames. **10 min:** timestamps and velocity. **10 min:** metric plane coordinates and failure cases. **10 min:** demonstrate the conveyor example or point tracking. | Estimate motion and recognize errors, missed detections, and plane-assumption limits. |
| **9.1: Planar visual feedback** | **10 min:** fixed camera and feature error. **15 min:** plane/image sensitivity and the known robot Jacobian. **15 min:** simple feedback law. **10 min:** worked example. | Predict corrective motion for a fixed-camera planar task. |
| **9.2: Eye-in-hand servoing** | **15 min:** camera-to-tool frames and camera motion. **15 min:** feature or image Jacobian and depth. **10 min:** simulation demonstration. **10 min:** feature count and degrees of freedom. | Connect image motion to robot motion when the camera is mounted on the arm. |
| **9.3: Integration and limitations** | **15 min:** run and inspect a visual-servo example. **15 min:** gain, delay, singularities, and feature loss. **10 min:** compare image-based and position-based servoing. **10 min:** review or optional preview. | Diagnose controller behavior and justify appropriate assumptions and measurements. |

Short activities can include predicting a projected point, tracing the coordinates of a calibration marker, inspecting a failed mask, or predicting the sign of camera motion from an image error.

## Camera and planar homography

For a 3D point \((X_c,Y_c,Z_c)\) expressed in the camera frame, the ideal pinhole model is

\[
u=f_x\frac{X_c}{Z_c}+c_x,\qquad
v=f_y\frac{Y_c}{Z_c}+c_y.
\]

For a point \((X,Y,0)\) on a known workspace plane, a homography relates plane and image coordinates:

\[
\alpha
\begin{bmatrix}u\\v\\1\end{bmatrix}
=
\underbrace{K\begin{bmatrix}r_1&r_2&t\end{bmatrix}}_{H_{I\leftarrow P}}
\begin{bmatrix}X\\Y\\1\end{bmatrix}.
\]

Here \(K\) is the intrinsic matrix, and \(r_1,r_2,t\) come from the plane-to-camera pose. The inverse mapping gives plane coordinates from image coordinates after homogeneous normalization.

Students can estimate an image-to-plane homography directly from corresponding points without separately solving for the camera's full pose. Use at least four well-distributed point pairs on the plane, with no three of the four collinear. More points can improve robustness. Keep separate points or distances for validation: four exact correspondences alone do not demonstrate accuracy elsewhere in the workspace.

Important distinctions:

- Camera intrinsics and lens distortion describe the camera; a planar homography describes the mapping for a particular plane and camera pose. Provide intrinsic calibration if the class will not perform it.
- Lens distortion is not generally represented by a homography. Use undistorted coordinates when appropriate, and state any simplified distortion assumptions.
- A rectified image is still measured in pixels. Define its pixels-per-unit scale and axis directions.
- A plane coordinate must be related to the robot-base frame, or measured directly in a plane frame whose relationship to the robot is known.
- A homography is valid for the specified plane and camera pose. An object's visible top or a tool marker at another height can produce a biased location estimate.
- For a moving eye-in-hand camera, the plane-to-image mapping changes with camera pose. It can be updated from a known camera pose or visible planar references, or the controller can work directly with image features.

OpenCV resources: [camera calibration and projection](https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html), [homographies](https://docs.opencv.org/4.x/d9/dab/tutorial_homography.html), and [geometric image transformations](https://docs.opencv.org/4.x/da/d6e/tutorial_py_geometric_transformations.html).

## Detection, tracking, and planar motion

A suitable first pipeline is:

1. Acquire or generate an image and apply the chosen camera or plane calibration.
2. Threshold a contrasting color or intensity range to obtain a mask.
3. Use connected components or contours to identify an object.
4. Compute a centroid, area, bounding box, and, when meaningful, orientation.
5. Associate the object or selected feature across frames.
6. Convert its location into plane coordinates and use timestamps to estimate velocity.
7. Report whether the feature was detected and handle missing or implausible measurements.

For known plane positions \(\mathbf p_k\) and actual timestamps,

\[
\hat{\mathbf v}_k =
\frac{\mathbf p_k-\mathbf p_{k-1}}{t_k-t_{k-1}}.
\]

Without calibration this is an image velocity, usually in pixels per second. With a metric plane mapping and valid plane assumptions it can be reported in meters per second or another physical unit. Frame-rate assumptions, jitter, and missed detections affect the result.

For a planar region under perspective, transforming the centroid measured in the original image is not generally identical to computing the centroid after rectifying the region. For a simple exercise, rectify the planar image or mask before computing a plane centroid, or track a well-defined point marker. Be explicit about what the reported feature represents.

A single blob centroid supports planar position feedback. Shape symmetry can make orientation ambiguous; a circle, for example, does not reveal its in-plane rotation. A classifier trained separately can supply a class label, but classification alone does not supply the object's centroid or a segmentation mask.

[OpenCV's contour-feature tutorial](https://docs.opencv.org/4.x/dd/d49/tutorial_py_contour_features.html) covers moments, centroid, area, and bounding boxes. Its [optical-flow tutorial](https://docs.opencv.org/4.x/d4/dee/tutorial_optical_flow.html) provides a point-tracking example.

## Visual-servoing connection

Begin with a fixed camera, a calibrated workspace plane, a planar arm, and a stationary target. Let \(\mathbf p_e(q)\) be the tool position and \(\mathbf p_t\) the measured target position in the same plane frame. A simple local velocity command is

\[
\dot q=-kJ_p(q)^{+}\bigl(\mathbf p_e(q)-\mathbf p_t\bigr),
\]

where \(J_p(q)\) maps joint velocities to planar tool velocity, \(J_p^{+}\) is a pseudoinverse or a suitable damped inverse, and \(k>0\) is a gain. The tool position may come from the robot model and encoders or from a visible tool marker, depending on the exercise.

This is a teaching model for the specified planar task, not a general guarantee of convergence. Students should inspect the effects of calibration error, limited velocity, singularity, sample rate, delay, and feature loss. Use a sensible stop or hold behavior when the target is not detected.

For eye-in-hand control, introduce image features \(s\), desired features \(s^\ast\), and the local image relation

\[
\dot s=L_s\,v_c,
\]

where \(L_s\) is the image or interaction Jacobian and \(v_c\) is the camera velocity. The camera-to-tool relationship and robot Jacobian connect camera velocity to joint velocity. Camera motion changes the view; the sign of image motion depends on the chosen frame and feature conventions. For a moving target, its motion also contributes to feature motion.

Choose the desired image feature from the desired tool pose or a reference view. The image center is not automatically the correct grasp or tool position when the camera is offset from the tool. One centroid has two scalar image coordinates; richer tasks need additional independent measurements or assumptions.

An introduction to image-based and position-based visual servoing is available in [Chaumette and Hutchinson's tutorial](https://web.mit.edu/amcp/OldFiles/drg/Chaumette_Part_I.pdf).

## Suggested assignments and evidence

The suggested assignments form one connected project. Supply starter code, a robot model, calibration targets, and an image generator or recorded sequences.

### Assignment A: calibrate, detect, and track

- Given an oblique view of a planar workspace and known reference points, estimate an image-to-plane homography.
- Validate the mapping with an independent known point or distance; document coordinate directions and units.
- Segment a contrasting object and report its centroid, area, and a simple shape or orientation measure when appropriate.
- Track the object through a sequence and estimate its planar velocity using timestamps.
- Compare position and velocity estimates with supplied ground truth; report missing detections and at least one limitation.

### Assignment B: planar visual servoing

- Use the vision output or a supplied feature detector with a simulated planar arm.
- Define a target and error in a consistent coordinate frame.
- Use the provided robot Jacobian and a basic feedback controller to command joint motion.
- Plot error over time and explain the effects of one changed condition, such as gain, initial position, delay, or feature loss.
- Demonstrate an appropriate stop or hold behavior if the target is unavailable.

**Optional extension:** introduce an eye-in-hand camera, recompute the relevant mapping as the camera moves or use a provided image Jacobian, and compare the behavior with the fixed-camera case.

Suggested evidence includes code or notebooks, annotated frames, a calibration check, position/velocity error plots, a visual-servo error plot, and a short engineering explanation. Use the same scene and units when comparing methods. Distinguish a genuinely missing detection from a zero-valued measurement.

## Synthetic image and video requirements

OpenCV can process NumPy image arrays generated in code as well as frames from an existing robot simulator or recorded camera. Synthetic examples provide known positions and repeatable scenarios without requiring camera hardware.

A minimal generator or provided dataset should support:

- A planar workspace with a stated physical size, coordinate frame, and visible calibration marks.
- Colored circles, rectangles, or other simple shapes with known position, size, and motion.
- A perspective mapping from the plane to an oblique camera image. Supply or derive the mapping consistently; keep the generator's ground truth separate from the student's estimated calibration.
- A reproducible sequence with explicit timestamps, including a stationary-target case for initial visual servoing.
- Ground truth for plane positions, velocities, marker coordinates, and object visibility. Include at least one independent calibration-check point.
- Simple variation in color, lighting, blur, partial occlusion, or detection loss for discussing robustness.
- An option to generate frames in memory or save a short sequence. Indexed lossless image frames plus timestamp metadata are a reliable baseline; video export may depend on available codecs.
- Reproducible random seeds where random variation is used.

For a wrist-camera extension, the generator must update the camera pose and plane-to-image mapping as the robot moves. A fixed homography cannot represent the entire moving-camera sequence.

A homography-based synthetic scene is a controlled planar model. It does not automatically simulate lens distortion, real reflections, sensor noise, three-dimensional object height, or real camera timing. Add these deliberately if needed, and include real imagery as a later comparison when available.

OpenCV's Python interface accepts NumPy image arrays. State the image dimensions, data type, and channel convention; in particular, convert appropriately if a simulator supplies RGB while an OpenCV operation is expecting a BGR-formatted image. [OpenCV drawing functions](https://docs.opencv.org/4.x/dc/da5/tutorial_py_drawing_functions.html) and [perspective transformations](https://docs.opencv.org/4.x/da/d6e/tutorial_py_geometric_transformations.html) are sufficient for a basic synthetic example.

## Docker and software integration requirements

**Status:** no course Dockerfile or dependency manifest was available in the inspected workspace. The receiving session must inspect the real repository and validate its actual environment before selecting package versions or changing the image.

1. Inventory the existing Docker base, operating system, architecture, Python interpreter, NumPy version, simulator, ROS/robotics packages if any, notebook/display system, and dependency lock or requirements files.
2. Ensure the course Docker image provides a compatible Python `cv2` import. Use the existing compatible installation if present; otherwise add OpenCV using the repository dependency-management method. Preserve a cohesive installation, particularly when compiled robotics bindings share OpenCV or NumPy dependencies.
3. If a Python OpenCV wheel is appropriate, choose **one** package from the OpenCV Python family. The packages share the `cv2` namespace; do not install multiple variants into the same environment. A headless package is a candidate for container or notebook workflows that do not use `cv2.imshow`. Choose a GUI-capable package only if the existing course workflow supports and needs native windows. See the [OpenCV Python package guidance](https://pypi.org/project/opencv-python-headless/).
4. Select and record a version compatible with the repository's actual Python, NumPy, operating system, architecture, and other packages. Do not assume that the newest release is compatible or overwrite existing pins without checking. If ROS or another simulator uses compiled image bindings, verify the selected Python/OpenCV/NumPy combination with those bindings.
5. Confirm whether optional modules such as ArUco are required before selecting a package variant. Availability depends on the chosen OpenCV version and build.
6. In a headless environment, display images through the course's existing notebook or viewer, or save image files. Do not rely on OpenCV native windows unless the container's display configuration has been verified.
7. Keep synthetic examples runnable without network access after setup and without physical camera hardware. Do not add PyTorch solely for this unit; neural-network training is separate.
8. Document where generated data and plots are stored, how files persist outside a container, and which image or video formats are actually supported.

Suggested compatibility checks for the receiving session after integrating OpenCV:

- Import `cv2` and NumPy in the **same interpreter used by the course**, and record their versions and interpreter path.
- Generate a small image array, draw a shape, apply a perspective warp, segment it, and recover a nonempty centroid.
- Run an existing robotics or simulation example to check that its imports and image interfaces still work.
- Generate and read a short timestamped image sequence; check video encoding separately only if the assignment requires video files.
- Verify the chosen image-display path in the actual course environment.

These are proposed checks for the existing repository; none were run against a course Docker image while preparing this brief.

## Reading and reference options

The unit can be taught without choosing Corke as the final textbook.

### Open resources

- **MIT robotics lecture:** cameras, color vision, blob detection, and a visual-servoing lab. [Cameras and color vision](https://courses.csail.mit.edu/6.141/spring2014/pub/lectures/Lec04-CamerasAndColorVision.pdf)
- **Carnegie Mellon robotics lab:** OpenCV contours, shape matching, optical flow, and tracking. [Cognitive Robotics Lab 7](https://www.cs.cmu.edu/afs/cs/academic/class/15494-s18/labs/lab7/lab7.html)
- **University of Maryland course:** an introductory robotics and perception course using image processing, OpenCV, and visual servoing. [Robotics and Perception](https://users.umiacs.umd.edu/~fermulcm/cmsc498F-828K/cmsc-498F-828K.htm)
- **OpenCV camera geometry:** [camera calibration and 3D reconstruction](https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html) and [homography tutorial](https://docs.opencv.org/4.x/d9/dab/tutorial_homography.html).
- **OpenCV features and tracking:** [contour features](https://docs.opencv.org/4.x/dd/d49/tutorial_py_contour_features.html) and [optical flow](https://docs.opencv.org/4.x/d4/dee/tutorial_optical_flow.html).
- **Visual servoing:** [Chaumette and Hutchinson, Visual Servo Control, Part I](https://web.mit.edu/amcp/OldFiles/drg/Chaumette_Part_I.pdf), for image-based and position-based formulations.
- **OpenCV packaging:** [OpenCV Python headless package documentation](https://pypi.org/project/opencv-python-headless/), including package variants and GUI limitations.

### Optional textbook reading

Peter Corke, *Robotics, Vision and Control: Fundamental Algorithms in Python*, third edition, 2023. These references are optional; the textbook has not been selected.

- Section 11.1: obtaining images; Section 11.6: mathematical morphology.
- Section 12.1: region features and object descriptions; Section 12.3: point features.
- Section 13.1–13.2: perspective camera and camera calibration; Section 13.6.2: planar homography.
- Chapter 15, especially Section 15.2.1–15.2.2: image motion and controlling feature motion. The diagrams on printed page 668 compare camera configurations and control structures.
- Optional extensions: Section 12.1.4 on deep-learning detection and Section 14.3–14.4 on stereo.

The book's Python examples use Corke's vision toolbox. The concepts can be adapted to OpenCV; the APIs are not identical.
