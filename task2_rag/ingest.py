"""Load PDF/text files -> recursive chunking -> embeddings -> ChromaDB (persisted on disk)."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from common.models import get_embeddings

COLLECTION = "datheon_rag"
DEFAULT_DB_DIR = Path(__file__).parent / "chroma_db"
SUPPORTED = {".pdf", ".txt", ".md"}


def collect_files(paths: Iterable[str | Path]) -> list[Path]:
    files: list[Path] = []
    for p in map(Path, paths):
        if p.is_dir():
            files.extend(sorted(f for f in p.rglob("*") if f.suffix.lower() in SUPPORTED))
        elif p.suffix.lower() in SUPPORTED:
            files.append(p)
        else:
            raise ValueError(f"Unsupported file type: {p}")
    if not files:
        raise ValueError("No PDF/TXT/MD files found.")
    return files


def load_documents(files: list[Path]) -> list[Document]:
    docs: list[Document] = []
    for f in files:
        loader = PyPDFLoader(str(f)) if f.suffix.lower() == ".pdf" else TextLoader(str(f), encoding="utf-8")
        for d in loader.load():
            d.metadata["source"] = f.name
            if f.suffix.lower() == ".pdf":  # PyPDFLoader pages are 0-indexed
                d.metadata["page_display"] = int(d.metadata.get("page", 0)) + 1
            docs.append(d)
    return docs


def split_documents(docs: list[Document], chunk_size: int = 1000, chunk_overlap: int = 150) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_documents(docs)  # metadata (source, page) is inherited by each chunk


def ingest_paths(paths: Iterable[str | Path], persist_dir: str | Path = DEFAULT_DB_DIR) -> int:
    """Rebuild the vector store from the given files/folders. Returns number of chunks stored."""
    chunks = split_documents(load_documents(collect_files(paths)))
    embeddings = get_embeddings()
    try:  # start clean so re-ingesting never creates duplicates
        Chroma(collection_name=COLLECTION, embedding_function=embeddings,
               persist_directory=str(persist_dir)).delete_collection()
    except Exception:
        pass
    Chroma.from_documents(chunks, embedding=embeddings, collection_name=COLLECTION,
                          persist_directory=str(persist_dir))
    return len(chunks)
