# Vendor Comparison & QuickBooks Sync

## Overview
This project compares vendor data from an Excel file against the vendor list stored in QuickBooks Desktop.
The tool identifies:
- Vendors in both Excel and QB with same data
- Vendors only in Excel (added to QB)
- Vendors only in QB
- Vendors with same ID but mismatched data

The program outputs a JSON report and includes a CLI and Windows executable.


## How to Run the CLI
To setup pre-commit hook (you only need to do this once):
```bash
poetry run python -m src.cli --workbook company_data.xlsx
```
or
```bash
python -m src.cli --workbook company_data.xlsx
```
This generates: comparison_report.json


## How to Build EXE
Install PyInstaller:
```bash
poetry add pyinstaller --group dev
```

## Build EXE:
```bash
poetry run pyinstaller --onefile --name vendor_compare src/cli.py
```
Executable appears in: dist/vendor_compare.exe

## Run EXE:
```bash
dist\vendor_compare.exe --workbook company_data.xlsx
```

## Example JSON
```bash
{
  "status": "success",
  "generated_at": "2025-12-03T19:34:14.860918+00:00",
  "added_vendors": [
    {
      "record_id": "555",
      "name": "Only Excel"
    }
  ],
  "conflicts": [
    {
      "record_id": "5",
      "reason": "data_mismatch",
      "excel_name": "Test-sid",
      "qb_name": "Piston Exports - test"
    },
    {
      "record_id": "99",
      "reason": "missing_in_excel",
      "excel_name": null,
      "qb_name": "only QB"
    }
  ],
  "same_vendors": 4,
  "error": null
}
```
