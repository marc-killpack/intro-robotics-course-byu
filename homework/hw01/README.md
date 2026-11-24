# HW01: ROS 2 setup and a joint-state publisher

Follow [the setup instructions](../../docs/setup.md) first. The written
assignment PDF supplied by the instructor defines the deliverables.

## 1. See RViz in your browser

Start Docker Desktop, then run these commands **on your computer**, from the
course repository folder:

```text
docker compose build
docker compose up -d
```

Open your usual web browser and visit:

**<http://localhost:6080/vnc.html?autoconnect=1&resize=scale>**

This is a local Linux desktop showing RViz. The Docker Desktop dashboard is
a different window. Wait for the robot to appear; the first startup builds
its package. If the slider window is hidden, move or minimize the main RViz
window. Move the head and both leg sliders. Select Move Camera and drag in
the 3D view; scroll to zoom. Save evidence of your setup working.

## 2. Switch to your publisher

Run this **on your computer** to recreate the course container with its
automatic slider publisher disabled:

```text
docker compose -f compose.yaml -f compose.publisher.yaml up -d --force-recreate
docker compose exec course bash
```

Refresh the browser page after recreation. RViz stays available. The second
command opens a **Linux shell inside the course container**. In that shell:

```bash
cd /workspace
python3 homework/hw01/joint_publisher.py
```

In publisher mode, robot links may not appear until your first valid joint
message arrives. Missing-transform messages before that first publication
do not mean the installation has failed.

Your released starter raises a labeled `NotImplementedError` until you
complete its two methods. Edit the file with your usual host editor; the
repository is mounted into `/workspace`, so you are editing the same file.
Stop your node with Ctrl+C before rerunning it after edits. You do not need
to rebuild the image or package after changing this standalone Python file.

The supplied class creates a publisher and a timer. `rclpy.spin(node)` lets
ROS invoke the timer callback every 0.1 seconds. First publish a fixed pose;
then compute changing positions from elapsed time. Repeating the same pose
holds the same picture. Changing the positions over time produces motion.
Use radians and stay within the supplied joint limits. A function named
`check_joint_positions` explains and checks those limits in `support.py`.

`/joint_states` reports the model's joint positions. `robot_state_publisher`
uses those states and the URDF to generate `/tf`; RViz displays the result.
This exercise animates a kinematic model; no motor controller is involved.

## 3. Inspect your messages

Open a **second host terminal**, enter the same repository folder, and run:

```text
docker compose exec course bash
```

In this second container shell, while your publisher runs:

```bash
ros2 topic echo /joint_states --once
ros2 topic hz /joint_states
ros2 topic info /joint_states --verbose
```

Stop the rate display with Ctrl+C. Approximate 10 Hz is expected; browser
rendering and host load can affect what you observe. Check that your node is
the **only publisher** on `/joint_states`. RViz and robot-state-publisher are
subscribers. If the robot jumps between poses, check for a second publisher.

Then plot the motion over time with PlotJuggler, in the same second shell:

```bash
ros2 run plotjuggler plotjuggler
```

In its window on the browser desktop:

1. Set **Buffer** to 30 seconds, so the plot keeps at least two periods.
2. Under **Streaming**, choose **ROS2 Topic Subscriber** and click **Start**.
3. Select `/joint_states` and click **OK**.
4. Drag `/joint_states/head_yaw/position` from the list on the left into the
   plot area.

Read the period and amplitude from the plot and compare them with your
`joint_positions` function. A "Telemetry reply error" line in the terminal
is expected: the course container blocks PlotJuggler's usage report.

Explain how names correspond to positions, what the timestamp means, and why
a timer is used. The provided scaffold handles setup and shutdown so the
student work stays focused on message contents and motion over time.

## 4. Finish and stop

Submit your code, setup evidence, message/rate evidence, a short explanation,
and your AI-use statement as described in the handout. Run this in a **host
terminal**, not inside the container:

```text
docker compose down
```

You may then close the browser tab and quit Docker Desktop. Closing the tab
alone does not stop the container. Your source files remain in this folder.
To return to the slider demo later:

```text
docker compose up -d --force-recreate
```

## References

- [ROS 2 Python publisher tutorial](https://docs.ros.org/en/jazzy/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Py-Publisher-And-Subscriber.html)
- [JointState message fields](https://docs.ros.org/en/jazzy/p/sensor_msgs/msg/JointState.html)
