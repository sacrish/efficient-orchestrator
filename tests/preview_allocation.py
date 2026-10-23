"""Create a local callback test page; it never sends a real chat message."""

import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fragment", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    template = (Path(__file__).parent / "fixtures" / "allocation-host.html").read_text(encoding="utf-8")
    args.output.write_text(template.replace("__FRAGMENT__", args.fragment.read_text(encoding="utf-8")), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
