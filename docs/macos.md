# Mac setup

These steps install Docker on a Mac. Afterward, return to the
[setup guide](setup.md#open-the-course-folder-and-a-terminal-in-vs-code),
which covers everything else. No XQuartz or other display software is needed.

1. Find your Mac's processor: Apple menu > **About This Mac**. "Chip: Apple
   M..." means **Apple Silicon**; "Processor: ... Intel" means **Intel**.
2. Install the matching **Docker Desktop for Mac** (Apple Silicon or Intel)
   from [Docker's instructions](https://docs.docker.com/desktop/setup/install/mac-install/),
   start it, and wait until it says the engine is running. It may ask for
   permission the first time.
3. Open a terminal: in VS Code choose **Terminal > New Terminal** (or press
   Ctrl+\`), or open the **Terminal** app (Cmd+Space, type Terminal, press
   Return).
4. Check the processor type and Docker:

   ```bash
   uname -m
   docker info --format '{{.OSType}}/{{.Architecture}}'
   docker compose version
   ```

   Apple Silicon should print `arm64`, then `linux/aarch64` (or
   `linux/arm64`). Intel should print `x86_64`, then `linux/x86_64` (or
   `linux/amd64`). The last line is a Compose version.

Then continue with the [setup guide](setup.md#open-the-course-folder-and-a-terminal-in-vs-code).
If something goes wrong, see [troubleshooting](troubleshooting.md).

Intel Macs are expected to work but have not yet been tested with this
course; please tell the instructor how setup went on yours.
