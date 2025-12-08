from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal

SourceLiteral = Literal["excel", "quickbooks"]
ConflictReason = Literal[
    "data_mismatch",  # same ID, different data
    "missing_in_excel",  # exists in QB but not in Excel
]


@dataclass(slots=True)
class Vendor:
    """Represents a Vendor synchronised between Excel and QuickBooks."""

    record_id: str
    name: str
    source: SourceLiteral  # "excel" or "quickbooks"

    def __repr__(self) -> str:
        return (
            f"Vendor(record_id={self.record_id!r}, "
            f"name={self.name!r}, source={self.source!r})"
        )


@dataclass(slots=True)
class Conflict:
    """Describes a discrepancy between Excel and QuickBooks vendor data."""

    record_id: str
    excel_name: str | None
    qb_name: str | None
    reason: ConflictReason


@dataclass(slots=True)
class ComparisonReport:
    """Holds comparison results + counts for JSON output."""

    excel_only: list[Vendor] = field(default_factory=list)  # to be added to QB
    qb_only: list[Vendor] = field(default_factory=list)  # exists only in QB
    conflicts: list[Conflict] = field(
        default_factory=list
    )  # both mismatch + missing_in_excel
    same_vendors: int = 0  # same ID + same data


__all__ = [
    "Vendor",
    "Conflict",
    "ComparisonReport",
    "ConflictReason",
    "SourceLiteral",
]
