import argparse
import sys

from src.configuration import load_config
from src.pipeline import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser."""
    parser = argparse.ArgumentParser(description="Four-format data recovery and validation")
    parser.add_argument("--config", default="config.json",
                        help="path to config.json (default: config.json)")
    return parser


def main() -> int:
    """Parse arguments, load the config, run the pipeline, and return an exit code."""
    args = build_parser().parse_args()
    try:
        config = load_config(args.config)
    except (FileNotFoundError, ValueError) as error:
        print(f"Configuration error: {error}", file=sys.stderr)
        return 2
    return run_pipeline(config)


if __name__ == "__main__":
    sys.exit(main())