from .excel_reader import extract_vendor_list
from .qb_gateway import fetch_vendor_list, add_vendor_list
from .comparer import compare_vendors  # or compare_payment_terms

excel_vendors = extract_vendor_list("company_data.xlsx")
# for i in excel_vendors:
#     print(i)

qb_vendors = fetch_vendor_list()
# for i in qb_vendors:
#     print(i)

report = compare_vendors(excel_vendors, qb_vendors)
print(report)


# 🔹 THIS is the “add Excel Only to QB” step:
if report.excel_only:
    print(f"Adding {len(report.excel_only)} Excel-only vendors to QuickBooks...")
    add_vendor_list(report.excel_only)
else:
    print("No Excel-only vendors to add.")
