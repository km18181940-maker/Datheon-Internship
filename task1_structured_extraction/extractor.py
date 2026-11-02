"""Extraction pipeline: prompt -> LLM -> strict Pydantic validation -> self-correcting retry."""
from __future__ import annotations

import json
import logging
import re
from typing import Callable, Type, TypeVar

from pydantic import BaseModel, ValidationError

from llm import complete_json
from prompts import build_messages

log = logging.getLogger("extractor")
T = TypeVar("T", bound=BaseModel)

LLMFn = Callable[[str, list[dict]], str]


def _strip_fences(raw: str) -> str:
    return re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip())


def extract(
    text: str,
    doc_type: str,
    schema: Type[T],
    provider: str = "openai",
    max_retries: int = 2,
    llm_fn: LLMFn | None = None,
) -> T:
    """Return a validated model instance, or raise ValueError after retries are exhausted."""
    call = llm_fn or (lambda system, msgs: complete_json(provider, system, msgs))
    system, messages = build_messages(doc_type, schema.model_json_schema(), text)

    last_error = ""
    for attempt in range(max_retries + 1):
        raw = call(system, messages)
        try:
            return schema.model_validate_json(_strip_fences(raw))
        except (ValidationError, json.JSONDecodeError) as e:
            last_error = str(e)
            log.warning("Attempt %d failed validation: %s", attempt + 1, last_error)
            messages = messages + [
                {"role": "assistant", "content": raw},
                {"role": "user", "content": f"That output was invalid:\n{last_error}\nReturn corrected JSON only."},
            ]
    raise ValueError(f"Extraction failed after {max_retries + 1} attempts: {last_error}")
