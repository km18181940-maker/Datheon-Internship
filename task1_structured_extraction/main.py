"""CLI: python main.py samples/invoice.txt --type invoice --provider gemini"""
import argparse
import logging
import sys

from dotenv import load_dotenv

from extractor import extract
from schemas import SCHEMAS


def main() -> int:
    load_dotenv()
    p = argparse.ArgumentParser(description="Extract validated JSON from unstructured documents.")
    p.add_argument("file")
    p.add_argument("--type", choices=SCHEMAS, required=True)
    p.add_argument("--provider", choices=["openai", "gemini"], default="gemini")
    p.add_argument("--out", help="Write JSON to this path instead of stdout")
    args = p.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    text = open(args.file, encoding="utf-8").read()
    try:
        result = extract(text, args.type, SCHEMAS[args.type], provider=args.provider)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    out = result.model_dump_json(indent=2)
    if args.out:
        open(args.out, "w", encoding="utf-8").write(out)
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
