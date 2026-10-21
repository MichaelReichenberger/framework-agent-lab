"""Demonstrate the handout's two rejected requests without changing pricing."""
import argparse
from hashlib import sha256
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from starter.agent import build_tools


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("target-service"))
    args = parser.parse_args()
    pricing = args.root / "orders/pricing.py"
    before = sha256(pricing.read_bytes()).hexdigest()
    tools = {tool.name: tool for tool in build_tools(args.root)}
    requests = [
        ("read_file", {"path": "../HANDOUT.md"}),
        ("edit_pricing", {"old": "Decimal", "new": "float"}),
    ]
    results = [tools[name].invoke(arguments) for name, arguments in requests]
    for result in results:
        print(result)
    unchanged = sha256(pricing.read_bytes()).hexdigest() == before
    if not unchanged or not all(result.startswith("ERROR:") for result in results):
        print("DENIAL CHECK FAILED", file=sys.stderr)
        return 1
    print("Pricing unverändert.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
