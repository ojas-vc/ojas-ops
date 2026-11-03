"""Multi-channel marketing campaign cadence and budget flighting example with scenario loading."""

from __future__ import annotations

__author__ = "Balu Varanasi"
__email__ = "balu@chitram.ai"


import sys
from pathlib import Path

from ojas_ops.scenarios import run_scenario


def main() -> None:
    data_dir = Path(__file__).parent / "data"
    scenario_path = (
        Path(sys.argv[1]) if len(sys.argv) > 1 else data_dir / "q4_omnichannel_campaign.json"
    )

    print(f"=== Ojas Ops: Multi-Channel Marketing Campaign Flighting ({scenario_path.name}) ===")
    run_scenario(scenario_path)


if __name__ == "__main__":
    main()
