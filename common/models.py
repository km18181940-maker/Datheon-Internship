"""One place to build chat + embedding models, so every task works with Gemini or OpenAI.

Pick the provider with LLM_PROVIDER=gemini|openai in .env (default: gemini).
"""
from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()


def provider_name(provider: str | None = None) -> str:
    return (provider or os.getenv("LLM_PROVIDER", "gemini")).lower()


def get_chat_model(provider: str | None = None, temperature: float = 0.0):
    p = provider_name(provider)
    if p == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), temperature=temperature)
    if p == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=os.getenv("GEMINI_CHAT_MODEL", "gemini-2.0-flash"), temperature=temperature
        )
    raise ValueError(f"Unknown LLM_PROVIDER: {p}")


def get_embeddings(provider: str | None = None):
    p = provider_name(provider)
    if p == "openai":
        from langchain_openai import OpenAIEmbeddings

        return OpenAIEmbeddings(model=os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small"))
    if p == "gemini":
        from langchain_google_genai import GoogleGenerativeAIEmbeddings

        return GoogleGenerativeAIEmbeddings(
            model=os.getenv("GEMINI_EMBED_MODEL", "models/text-embedding-004")
        )
    raise ValueError(f"Unknown LLM_PROVIDER: {p}")
