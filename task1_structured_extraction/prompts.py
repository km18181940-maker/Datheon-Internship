"""Parameterized prompt templates with few-shot examples."""
import json

SYSTEM_TEMPLATE = """You are a precise document-extraction engine.
Task: extract a {doc_type} from the user's raw text.

Rules:
- Output ONLY one JSON object. No markdown, no commentary.
- It must conform to this JSON Schema:
{schema}
- Never invent data. If an optional field is missing, use null.
- Dates must be ISO format (YYYY-MM-DD) unless the schema says otherwise.
- Numbers must be plain numbers (no currency symbols or thousands separators).
"""

FEW_SHOT = {
    "invoice": (
        "INVOICE #A-17\nAcme Tools Ltd\nBill to: Zed Corp\nDate: March 3, 2026  Due: April 2, 2026\n"
        "2 x Hammer @ $10.00 = $20.00\nSubtotal $20.00  Tax $2.00  Total $22.00 USD",
        {
            "invoice_number": "A-17", "vendor_name": "Acme Tools Ltd", "customer_name": "Zed Corp",
            "invoice_date": "2026-03-03", "due_date": "2026-04-02", "currency": "USD",
            "line_items": [{"description": "Hammer", "quantity": 2, "unit_price": 10.0, "total": 20.0}],
            "subtotal": 20.0, "tax": 2.0, "total": 22.0,
        },
    ),
    "resume": (
        "Sara Lee | sara@example.com | Lahore\nSkills: Python, SQL\n"
        "Data Analyst, Foo Inc, Jan 2022 - Present\nBS Computer Science, FAST, 2021",
        {
            "full_name": "Sara Lee", "email": "sara@example.com", "phone": None, "location": "Lahore",
            "skills": ["Python", "SQL"],
            "experience": [{"company": "Foo Inc", "title": "Data Analyst", "start_date": "2022-01",
                            "end_date": None, "summary": None}],
            "education": [{"institution": "FAST", "degree": "BS Computer Science", "graduation_year": 2021}],
        },
    ),
}


def build_messages(doc_type: str, schema_json: dict, text: str) -> tuple[str, list[dict]]:
    system = SYSTEM_TEMPLATE.format(doc_type=doc_type, schema=json.dumps(schema_json, indent=2))
    ex_in, ex_out = FEW_SHOT[doc_type]
    messages = [
        {"role": "user", "content": f"Document:\n{ex_in}"},
        {"role": "assistant", "content": json.dumps(ex_out)},
        {"role": "user", "content": f"Document:\n{text}"},
    ]
    return system, messages
