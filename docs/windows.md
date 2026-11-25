# Windows setup

These steps install Docker on Windows. Afterward, return to the
[setup guide](setup.md#open-the-course-folder-and-a-terminal-in-vs-code),
which covers everything else.

1. Install **Docker Desktop for Windows** following
   [Docker's instructions](https://docs.docker.com/desktop/setup/install/windows-install/).
   When asked, use the **WSL 2** backend (WSL is Windows' built-in way to
   run Linux) and **Linux containers**. Restart Windows if the installer asks.
2. Start Docker Desktop from the Start menu and wait until it says the engine
   is running.
3. Open a terminal. Either open the course folder in VS Code and choose
   **Terminal > New Terminal** (or press Ctrl+\`), or press the Windows key,
   type **PowerShell**, and press Enter. Both give you PowerShell; its prompt
   starts with `PS`.
4. Check WSL and Docker:

   ```powershell
   wsl --status
   docker version
   docker compose version
   ```

   `wsl --status` should mention WSL version 2. `docker version` must show
   both a `Client:` and a `Server:` section;
   [setup](setup.md#check-that-docker-is-running) shows a correct example
   and explains what to do if the `Server:` part is missing.

Then continue with the [setup guide](setup.md#open-the-course-folder-and-a-terminal-in-vs-code).
If something goes wrong, see [troubleshooting](troubleshooting.md).
