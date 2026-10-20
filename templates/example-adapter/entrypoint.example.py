"""Placeholder entrypoint — replace with your framework's real native entrypoint.

The launched process must own the whole research flow (ideation, experiments,
comparison, selection, final artifacts). This file contains no evaluation
logic (rules §7.2) — it is a skeleton showing where things go.
"""
import os
from pathlib import Path


def main() -> None:
    # Print the native marker as early as possible, from inside THIS process:
    marker = os.environ.get(
        "FRAMEWORK_NATIVE_LOG_MARKER", "FRAMEWORK_NATIVE_LOG_MARKER"
    )
    print(marker, flush=True)

    contract = Path("/workspace/input/contract.md")
    if contract.exists():
        print(f"[myframework] loaded contract: {contract.name}")

    # TODO(replace-me): run your framework's actual pipeline here.
    # 1. write and lock research_idea.json BEFORE the first experiment
    # 2. run 2-4 materially different experiments (contract's experiment budget)
    # 3. compare on the designated validation metric, select, promote
    # 4. write final_report.md and the topic payload into the workspace root
    #    (payload formats: rules §5.3 / contracts/)


if __name__ == "__main__":
    main()