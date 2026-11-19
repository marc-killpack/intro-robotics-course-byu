# Windows setup and validation

## Student setup

1. Install Docker Desktop for Windows from
   [Docker's instructions](https://docs.docker.com/desktop/setup/install/windows-install/).
   Use its WSL 2 backend and Linux containers. Complete any requested Windows
   restart before testing the course. Follow the vendor's current supported
   Windows/WSL requirements.
2. Start Docker Desktop and wait for the engine. In PowerShell, check:

   ```powershell
   wsl --status
   docker version
   docker compose version
   ```

   Docker must report a server as well as a client. The tested machine uses
   an x64 CPU and WSL version 2.
3. Open PowerShell in the cloned **student repository** folder, then follow
   [the common setup guide](setup.md). In particular, **open the RViz web
   address in your browser** after `docker compose up -d`.
4. Source files edited in a Windows editor are shared with `/workspace`.
   `.gitattributes` preserves LF for Linux shell scripts. Existing clones
   whose `docker/start-gui.sh` has CRLF may need its line endings changed to
   LF in the editor before rebuilding. No host ROS installation or X server
   is required by this path.

If Docker updates while you work, wait for it to finish and restart its
engine. Run `docker compose up -d` again and refresh the browser page.
If sliders seem absent, check behind the main RViz window. To stop, use
`docker compose down` in PowerShell, then quit Docker Desktop if desired.

## Observed instructor result, November 12, 2026

- Windows x64, OS build 26200; WSL 2 backend.
- Initial Docker engine/client 29.2.1, Compose 5.1.0.
- Docker Desktop updated during validation. Afterward: engine/client 29.9.3,
  Compose 5.7.0. The course container was recreated successfully.
- Native image architecture: `linux/amd64`.
- Initial image build: 195 seconds. Initial robot package build: about
  39 seconds; a later cached package build: about 8 seconds including colcon
  overhead. These timings are machine-specific observations.
- RViz started with OpenGL 4.5 using Mesa llvmpipe software rendering.
- Instructor observed the robot, all three sliders, and camera orbit/zoom.
- Slider window initially appeared **behind RViz**; revealing it resolved
  the apparent missing controls.
- A read-only ROS probe matched all three joint positions to their TF
  rotations and verified the fixed head-to-eye transform. The sampled head
  position was approximately 0.6365 radians.
- One running-container sample used about 302 MiB; this excludes Docker/WSL
  overhead and is not a minimum-memory specification or performance benchmark.

## Revised HW01 checks, November 12, 2026

The rebuilt image was tested in isolated temporary containers with no host
browser port published. Default mode started the slider publisher,
robot-state-publisher, and RViz (OpenGL 4.5). Publisher mode started RViz and
robot-state-publisher with the slider publisher absent. The actual HW01
instructor node produced 25 bounded, named messages at 10.00 Hz with changing
head positions and only one publisher. Both stripped student methods retained
their expected homework-labeled errors. The temporary containers were removed.

These are launch/message checks. The general Matplotlib arm viewer has
offscreen numerical/widget checks, while its interactive graphics performance
and other host configurations still need hands-on validation.
