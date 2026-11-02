"""
  python -m task2_rag.cli ingest task2_rag/docs
  python -m task2_rag.cli ask "How many remote days are allowed?"
  python -m task2_rag.cli chat
"""
import argparse

from task2_rag.ingest import DEFAULT_DB_DIR, ingest_paths
from task2_rag.rag import RAG, source_label


def show(rag: RAG, question: str) -> None:
    docs, tokens = rag.ask_stream(question)
    print("\nAnswer: ", end="", flush=True)
    for t in tokens:
        print(t, end="", flush=True)
    print("\n\nSources:")
    for s in dict.fromkeys(source_label(d) for d in docs):
        print(f"  - {s}")
    print()


def main() -> None:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    i = sub.add_parser("ingest"); i.add_argument("paths", nargs="+")
    a = sub.add_parser("ask"); a.add_argument("question")
    sub.add_parser("chat")
    args = p.parse_args()

    if args.cmd == "ingest":
        n = ingest_paths(args.paths)
        print(f"Indexed {n} chunks into {DEFAULT_DB_DIR}")
    elif args.cmd == "ask":
        show(RAG(), args.question)
    else:
        rag = RAG()
        print("Ask about your documents (type 'exit' to quit).")
        while (q := input("\nYou: ").strip()).lower() not in {"exit", "quit"}:
            if q:
                show(rag, q)


if __name__ == "__main__":
    main()
