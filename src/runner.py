from __future__ import annotations

from pathlib import Path
from typing import List

from . import comparer, excel_reader, qb_gateway
from .models import Vendor

DEFAULT_REPORT_NAME = "comparison_report.json"


def run_vendor_sync(
    company_file: str,
    workbook_path: str,
    *,
    output_path: str | None = None,
) -> Path:
    """
    Orchestrate the vendor comparison:

    1. Read vendors from the Excel workbook.
    2. Read vendors from QuickBooks.
    3. Compare Excel vs QB vendors and write a JSON report.
    4. Attempt to add Excel-only vendors to QuickBooks.
    """

    report_path = Path(output_path) if output_path else Path(DEFAULT_REPORT_NAME)

    # 1. Excel vendors
    excel_vendors: List[Vendor] = excel_reader.extract_vendor_list(Path(workbook_path))

    # 2. QuickBooks vendors
    qb_vendors: List[Vendor] = qb_gateway.fetch_vendor_list(company_file)

    # 3. Compare and write JSON (comparer handles JSON writing)
    comparison = comparer.compare_vendors(
        excel_vendors,
        qb_vendors,
        json_path=str(report_path),
    )

    # 4. Try to add Excel-only vendors to QB, but don't crash if QB refuses
    if comparison.excel_only:
        try:
            qb_gateway.add_vendor_list(comparison.excel_only)
        except Exception as exc:
            print(f"Warning: failed to add Excel-only vendors to QuickBooks: {exc}")

    return report_path


__all__ = ["run_vendor_sync", "DEFAULT_REPORT_NAME"]
