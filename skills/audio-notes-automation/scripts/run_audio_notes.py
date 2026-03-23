from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    src_dir = repo_root / "src"
    env = os.environ.copy()
    current_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(src_dir) if not current_pythonpath else str(src_dir) + os.pathsep + current_pythonpath
    command = [sys.executable, "-m", "audio_notes_automation", *sys.argv[1:]]
    subprocess.run(command, cwd=repo_root, env=env, check=True)


if __name__ == "__main__":
    main()

