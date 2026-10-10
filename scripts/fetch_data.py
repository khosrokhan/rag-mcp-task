from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

REPO = "https://github.com/OWASP/CheatSheetSeries.git"
DEST = Path("data/cheatsheets")


def main() -> None:
    DEST.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path("data/_owasp_repo")
    if tmp.exists():
        shutil.rmtree(tmp)
    subprocess.run(["git", "clone", "--depth", "1", REPO, str(tmp)], check=True)
    DEST.mkdir(parents=True, exist_ok=True)
    for p in (tmp / "cheatsheets").glob("*.md"):
        shutil.copy2(p, DEST / p.name)
    shutil.rmtree(tmp)
    print(f"Downloaded {len(list(DEST.glob('*.md')))} cheat sheets into {DEST}")


if __name__ == "__main__":
    main()
