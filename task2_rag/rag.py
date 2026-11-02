"""Retrieval-augmented QA that answers ONLY from the indexed documents, with page citations."""
from __future__ import annotations

from pathlib import Path
from typing import Iterator

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from common.models import get_chat_model, get_embeddings
from task2_rag.ingest import COLLECTION, DEFAULT_DB_DIR

NOT_FOUND = "I couldn't find that in the provided documents."

PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You answer questions strictly using the CONTEXT below. Do not use outside knowledge.\n"
     f"If the context does not contain the answer, reply exactly: \"{NOT_FOUND}\"\n"
     "Be concise. After each claim, cite its source in square brackets exactly as the context "
     "labels it, e.g. [handbook.pdf, p.4]."),
    ("human", "CONTEXT:\n{context}\n\nQUESTION: {question}"),
])


def source_label(doc: Document) -> str:
    name = doc.metadata.get("source", "unknown")
    page = doc.metadata.get("page_display")
    return f"{name}, p.{page}" if page else name


def format_context(docs: list[Document]) -> str:
    return "\n\n".join(f"[{source_label(d)}]\n{d.page_content}" for d in docs)


class RAG:
    def __init__(self, persist_dir: str | Path = DEFAULT_DB_DIR, k: int = 4):
        store = Chroma(collection_name=COLLECTION, embedding_function=get_embeddings(),
                       persist_directory=str(persist_dir))
        self.retriever = store.as_retriever(search_kwargs={"k": k})
        self.chain = PROMPT | get_chat_model() | StrOutputParser()

    def ask_stream(self, question: str) -> tuple[list[Document], Iterator[str]]:
        """Return (retrieved docs, token generator). Used by the CLI and the Streamlit UI."""
        docs = self.retriever.invoke(question)
        tokens = self.chain.stream({"context": format_context(docs), "question": question})
        return docs, tokens

    def ask(self, question: str) -> tuple[str, list[str]]:
        docs, tokens = self.ask_stream(question)
        answer = "".join(tokens)
        sources = list(dict.fromkeys(source_label(d) for d in docs))  # de-duplicated, ordered
        return answer, sources
