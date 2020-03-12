import argparse

from .config import load_config
from .discount_check import get_discounts


def get_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="")

    parser.add_argument(
        "--config",
        "-c",
        default="config.yml",
        help="Configuration file location for "
    )

    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        help="Enable debug mode (no email will be sent)."
    )

    return parser


def main() -> None:
    args = get_cli_parser().parse_args()
    config = load_config(args.config)

    get_discounts(args, config)


if __name__ == "__main__":
    main()
