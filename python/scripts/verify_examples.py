"""Verification script to test all domain examples end-to-end."""

import subprocess
import sys
from pathlib import Path

EXAMPLES = [
    "academic_timetabling",
    "basic_scheduling",
    "event_run_sheets",
    "festival_calendar",
    "film_production",
    "manufacturing",
    "marketing_flighting",
    "nurse_rostering",
]


def main() -> int:
    root_dir = Path(__file__).resolve().parent.parent
    examples_dir = root_dir / "examples"
    failed = []

    print("==================================================")
    print(" Verifying Ojas Ops Domain Examples")
    print("==================================================")

    for ex in EXAMPLES:
        script = examples_dir / ex / "main.py"
        if not script.exists():
            print(f"[-] {ex}: main.py NOT FOUND")
            failed.append(ex)
            continue

        print(f"[*] Running example: {ex}...", end=" ", flush=True)
        res = subprocess.run(
            [sys.executable, str(script)],
            cwd=str(root_dir),
            capture_output=True,
            text=True,
        )

        if res.returncode == 0:
            print("PASSED")
        else:
            print("FAILED")
            print(res.stderr)
            failed.append(ex)

    print("==================================================")
    if failed:
        print(f"FAILED {len(failed)}/{len(EXAMPLES)} examples: {', '.join(failed)}")
        return 1
    else:
        print(f"ALL {len(EXAMPLES)} EXAMPLES PASSED SUCCESSFULLY!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
