from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
BUILD_SCRIPT = ROOT / "build_site.py"
VAULT = ROOT.parent / "obsidian_vault" / "stock"
CHECK_INTERVAL_SECONDS = int(os.getenv("STOCK_HOMEPAGE_BUILD_INTERVAL", "60"))


def latest_mtime(path: Path) -> float:
    if not path.exists():
        return 0.0
    if path.is_file():
        return path.stat().st_mtime

    latest = path.stat().st_mtime
    for child in path.rglob("*"):
        try:
            latest = max(latest, child.stat().st_mtime)
        except OSError:
            continue
    return latest


def current_signature() -> tuple[float, float]:
    return (latest_mtime(BUILD_SCRIPT), latest_mtime(VAULT))


def run_build() -> bool:
    print(f"[stock-homepage-builder] running {BUILD_SCRIPT}", flush=True)
    result = subprocess.run([sys.executable, str(BUILD_SCRIPT)], cwd=ROOT)
    if result.returncode == 0:
        print("[stock-homepage-builder] build completed", flush=True)
        return True

    print(
        f"[stock-homepage-builder] build failed with exit code {result.returncode}",
        flush=True,
    )
    return False


def main() -> None:
    last_built_signature: tuple[float, float] | None = None

    while True:
        signature = current_signature()
        if signature != last_built_signature:
            if run_build():
                last_built_signature = signature

        if os.getenv("STOCK_HOMEPAGE_BUILD_LOOP_ONCE") == "1":
            return

        time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
