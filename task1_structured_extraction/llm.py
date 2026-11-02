"""Thin provider layer: OpenAI, Gemini, or an offline mock for tests."""
from __future__ import annotations

import os


def complete_json(provider: str, system: str, messages: list[dict]) -> str:
    if provider == "openai":
        from openai import OpenAI

        client = OpenAI()  # reads OPENAI_API_KEY
        resp = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0,
            response_format={"type": "json_object"},
            messages=[{"role": "system", "content": system}, *messages],
        )
        return resp.choices[0].message.content

    if provider == "gemini":
        import google.generativeai as genai

        genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
        model = genai.GenerativeModel(
            os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
            system_instruction=system,
            generation_config={"temperature": 0, "response_mime_type": "application/json"},
        )
        contents = [
            {"role": "model" if m["role"] == "assistant" else "user", "parts": [m["content"]]}
            for m in messages
        ]
        return model.generate_content(contents).text

    raise ValueError(f"Unknown provider: {provider}")
