from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Dict, Iterable

from .models import Vendor, Conflict, ComparisonReport


def compare_vendor_terms(  # keep this name to match the original spec
    excel_terms: Iterable[Vendor],
    qb_terms: Iterable[Vendor],
    json_path: str = "comparison_report.json",
) -> ComparisonReport:
    """
    Compare Excel vendor data with QuickBooks vendor data and write a JSON report
    matching the professor's sample format.
    """

    # Index by record_id for O(1) lookups
    excel_by_id: Dict[str, Vendor] = {v.record_id: v for v in excel_terms}
    qb_by_id: Dict[str, Vendor] = {v.record_id: v for v in qb_terms}

    report = ComparisonReport()

    # --- 1) Same ID (intersection) -> same_terms or data_mismatch conflicts ---
    shared_ids = excel_by_id.keys() & qb_by_id.keys()
    for rid in shared_ids:
        e = excel_by_id[rid]
        q = qb_by_id[rid]

        if e.name == q.name:
            # Same ID and same data
            report.same_vendors += 1
        else:
            # Same ID but different data
            report.conflicts.append(
                Conflict(
                    record_id=rid,
                    excel_name=e.name,
                    qb_name=q.name,
                    reason="data_mismatch",
                )
            )

    # --- 2) Excel Only: present in Excel, not in QB ---
    for rid, v in excel_by_id.items():
        if rid not in qb_by_id:
            report.excel_only.append(v)
            # NOTE: these are NOT conflicts in the sample JSON
            # They appear under "added_vendors" instead.

    # --- 3) QB Only: present in QB, not in Excel -> missing_in_excel conflict ---
    for rid, v in qb_by_id.items():
        if rid not in excel_by_id:
            report.qb_only.append(v)
            report.conflicts.append(
                Conflict(
                    record_id=rid,
                    excel_name=None,
                    qb_name=v.name,
                    reason="missing_in_excel",
                )
            )

    # --- Build JSON structure that matches professor's example ---

    def vendor_to_json(v: Vendor) -> dict:
        return {
            "record_id": v.record_id,
            "name": v.name,
            # payment-terms example has only these fields in "added_vendors"
        }

    def conflict_to_json(c: Conflict) -> dict:
        return {
            "record_id": c.record_id,
            "reason": c.reason,
            "excel_name": c.excel_name,
            "qb_name": c.qb_name,
        }

    json_data = {
        "status": "success",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "added_vendors": [vendor_to_json(v) for v in report.excel_only],
        "conflicts": [conflict_to_json(c) for c in report.conflicts],
        "same_vendors": report.same_vendors,
        "error": None,
    }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2)

    print(f"JSON report saved to {json_path}")
    return report


# For convenience if you still want this name:
compare_vendors = compare_vendor_terms

__all__ = ["compare_vendor_terms", "compare_vendors"]
