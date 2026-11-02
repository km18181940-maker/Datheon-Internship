"""Pydantic schemas that define the *only* JSON shapes the LLM output may take."""
from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, model_validator


class LineItem(BaseModel):
    description: str
    quantity: float = Field(gt=0)
    unit_price: float = Field(ge=0)
    total: float = Field(ge=0)


class Invoice(BaseModel):
    invoice_number: str
    vendor_name: str
    customer_name: Optional[str] = None
    invoice_date: date
    due_date: Optional[date] = None
    currency: str = Field(min_length=3, max_length=3, description="ISO 4217 code, e.g. USD")
    line_items: list[LineItem] = Field(min_length=1)
    subtotal: float = Field(ge=0)
    tax: float = Field(ge=0, default=0)
    total: float = Field(ge=0)

    @model_validator(mode="after")
    def totals_must_add_up(self) -> "Invoice":
        if abs(self.subtotal + self.tax - self.total) > 0.02:
            raise ValueError(
                f"subtotal ({self.subtotal}) + tax ({self.tax}) != total ({self.total})"
            )
        return self


class Experience(BaseModel):
    company: str
    title: str
    start_date: str = Field(description="YYYY-MM")
    end_date: Optional[str] = Field(default=None, description="YYYY-MM or null if current")
    summary: Optional[str] = None


class Education(BaseModel):
    institution: str
    degree: str
    graduation_year: Optional[int] = Field(default=None, ge=1950, le=2100)


class Resume(BaseModel):
    full_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    skills: list[str] = Field(min_length=1)
    experience: list[Experience] = []
    education: list[Education] = []


SCHEMAS = {"invoice": Invoice, "resume": Resume}
