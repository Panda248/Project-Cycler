"""

Features:

Core:
Start a looping timer.
Everytime the timer ends, we want to kill the current project process
and start the next project in the list.

Extra:
We want some TUI that provides status on the current project, time until next project,
and startup time.

On startup:
Go through all folders in ./projects (shallow)
In each folder, look for a startup file (tbd)
Add each project's startup filepath into a list in memory
Begin a timer in the main loop and start a child process that runs the first project

On Loop:
Kill the child process, increment, startup next project

"""

import os
import argparse
import subprocess
import time
from pathlib import Path


class ProjectCycler:
    def __init__(self, project_dir="./projects", interval_seconds=60):
        self.project_dir = project_dir
        self.interval_seconds = interval_seconds
        self.startup_files = []
        self.project_directorys = []
        self.current_index = 0
        self.current_process = None
        self.next_switch_at = interval_seconds

    def _find_startup_file(self, project_path: str | Path):
        # TODO: define actual startup-file convention for each project.
        candidates = ['run.bat']
        for candidate in candidates:
            path = os.path.join(project_path, candidate)
            if os.path.isfile(path):
                return path
        return None

    def onstartup(self):
        if not os.path.isdir(self.project_dir):
            raise FileNotFoundError(
                f"Project directory not found: {self.project_dir}")

        for entry in sorted(os.listdir(self.project_dir)):
            project_path = os.path.join(self.project_dir, entry)
            if not os.path.isdir(project_path):
                print("path in project_dir doesnt exist as a path???")
                continue

            print(f"Processing project: {entry} at {project_path}")

            startup_file = self._find_startup_file(project_path)
            if startup_file is not None:
                self.startup_files.append(startup_file)
                self.project_directorys.append(project_path)
                print(
                    f"Startup File Found: {startup_file}, added in position {len(self.startup_files)}")
            else :
                print("WARNING: NO STARTUP FILE FOUND. Skipping...")

        if not self.startup_files:
            raise RuntimeError(
                f"No startup files found under {self.project_dir}")

        self.current_index = 0
        self.current_process = self._start_project(self.current_index)
        self.next_switch_at = time.monotonic() + self.interval_seconds

    def _start_project(self, i: int):
        start_file = self.startup_files[i]
        proj_dir = self.project_directorys[i]
        print(f"Running {start_file} from {proj_dir}")
        return subprocess.Popen(
            ["powershell", "./run.bat", "pause"],
            cwd=proj_dir,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
        )

    def _stop_project(self):
        process = self.current_process
        if process is None:
            return

        self.current_process = None
        if process.poll() is not None:
            return

        result = subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0 and process.poll() is None:
            raise RuntimeError(
                f"Could not stop project process tree for PID {process.pid}: "
                f"{result.stderr.strip()}"
            )
        process.wait()

    def onloop(self):
        self._stop_project()

        self.current_index = (self.current_index + 1) % len(self.startup_files)
        self.current_process = self._start_project(self.current_index)
        self.next_switch_at = time.monotonic() + self.interval_seconds

    def core(self):
        self.onstartup()

        try:
            while True:
                if time.monotonic() >= self.next_switch_at:
                    self.onloop()
                time.sleep(0.2)
        finally:
            self._stop_project()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Cycle through project startup scripts at a fixed interval."
    )
    parser.add_argument(
        "--delay",
        "-d",
        type=float,
        default=10,
        metavar="SECONDS",
        help="time to run each project before switching (default: 10 seconds)",
    )
    args = parser.parse_args()

    if args.delay <= 0:
        parser.error("--delay must be greater than zero")

    ProjectCycler(interval_seconds=args.delay).core()
