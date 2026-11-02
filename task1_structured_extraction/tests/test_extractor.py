"""Offline tests: no API key needed. Run with `pytest`."""
import json
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from extractor import extract  # noqa: E402
from schemas import Invoice  # noqa: E402

GOOD = {
    "invoice_number": "X1", "vendor_name": "V", "invoice_date": "2026-01-01", "currency": "USD",
    "line_items": [{"description": "a", "quantity": 1, "unit_price": 10, "total": 10}],
    "subtotal": 10, "tax": 1, "total": 11,
}


def test_valid_output_parses():
    inv = extract("text", "invoice", Invoice, llm_fn=lambda s, m: json.dumps(GOOD))
    assert inv.total == 11


def test_retry_recovers_from_bad_totals():
    bad = {**GOOD, "total": 99}
    replies = iter([json.dumps(bad), "```json\n" + json.dumps(GOOD) + "\n```"])
    inv = extract("text", "invoice", Invoice, llm_fn=lambda s, m: next(replies))
    assert inv.total == 11


def test_gives_up_after_retries():
    with pytest.raises(ValueError):
        extract("text", "invoice", Invoice, max_retries=1, llm_fn=lambda s, m: "not json")
