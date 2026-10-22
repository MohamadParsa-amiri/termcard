import argparse
import os
from pathlib import Path

from . import __version__
from .cli import FlashcardApp

DEFAULT_DATA = Path.home() / ".termcard" / "decks.json"
DEMO_DECK = Path(__file__).resolve().parent / "data" / "demo_deck.json"


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="termcard",
        description="Spaced-repetition flashcards in your terminal, with first-class RTL (Persian) support.",
    )
    parser.add_argument(
        "--data", type=Path, default=None, metavar="PATH",
        help="Path to the decks JSON file (default: ~/.termcard/decks.json or $TERMCARD_DATA)",
    )
    parser.add_argument(
        "--demo", action="store_true",
        help="Seed a small Spanish demo deck on first run, then start the app",
    )
    parser.add_argument("--version", action="version", version=f"termcard {__version__}")
    args = parser.parse_args(argv)

    data_path = args.data or Path(os.environ.get("TERMCARD_DATA", DEFAULT_DATA))

    if args.demo and not data_path.exists():
        data_path.parent.mkdir(parents=True, exist_ok=True)
        data_path.write_text(DEMO_DECK.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"  Demo deck seeded -> {data_path}")

    FlashcardApp(data_path).run()


if __name__ == "__main__":
    main()
