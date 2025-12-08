"""Command-line interface for the QuickBooks/Excel vendor comparison tool."""

from __future__ import annotations

import argparse
import sys

from src.runner import run_vendor_sync


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Compare vendor data between Excel and QuickBooks, "
            "write a JSON report, and attempt to add Excel-only vendors to QuickBooks."
        )
    )

    parser.add_argument(
        "--workbook",
        required=True,
        help="Path to the Excel workbook containing vendor data "
        "(e.g. company_data.xlsx).",
    )

    parser.add_argument(
        "--output",
        default="comparison_report.json",
        help="JSON output path (default: comparison_report.json).",
    )

    args = parser.parse_args(argv)

    # company_file: empty string = currently open company in QuickBooks
    json_path = run_vendor_sync(
        "",
        args.workbook,
        output_path=args.output,
    )

    print(f"Report written to {json_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
