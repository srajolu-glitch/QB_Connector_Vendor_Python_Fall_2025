from __future__ import annotations
import xml.etree.ElementTree as ET
from contextlib import contextmanager
from typing import Iterator, List

try:
    import win32com.client
except ImportError:
    win32com = None

from .models import Vendor

APP_NAME = "Quickbooks Connector"


def _require_win32com() -> None:
    if win32com is None:
        raise RuntimeError("pywin32 is required to communicate with QuickBooks")


@contextmanager
def _qb_session() -> Iterator[tuple[object, object]]:
    _require_win32com()
    session = win32com.client.Dispatch("QBXMLRP2.RequestProcessor")
    session.OpenConnection2("", APP_NAME, 1)
    ticket = session.BeginSession("", 0)
    try:
        yield session, ticket
    finally:
        try:
            session.EndSession(ticket)
        finally:
            session.CloseConnection()


def _send_qbxml(qbxml: str) -> ET.Element:
    with _qb_session() as (session, ticket):
        # print("\n--- QBXML SENT ---")
        # print(qbxml)
        raw_response = session.ProcessRequest(ticket, qbxml)
        # print("\n--- QBXML RESPONSE ---")
        # print(raw_response)
    return _parse_response(raw_response)


# def _parse_response(raw_xml: str) -> ET.Element:
#     root = ET.fromstring(raw_xml)
#     response = root.find(".//*[@statusCode]")
#     if response is None:
#         raise RuntimeError("QuickBooks response missing status information")
#     status_code = int(response.get("statusCode", "0"))
#     status_message = response.get("statusMessage", "")
#     if status_code not in (0, 1):
#         raise RuntimeError(f"QuickBooks Error {status_code}: {status_message}")
#     return root


def _parse_response(raw_xml: str) -> ET.Element:
    root = ET.fromstring(raw_xml)
    response = root.find(".//*[@statusCode]")
    if response is None:
        raise RuntimeError("QuickBooks response missing status information")

    status_code_str = response.get("statusCode", "0")
    try:
        status_code = int(status_code_str)
    except ValueError:
        status_code = 0

    status_message = response.get("statusMessage", "")

    # 👇 Treat "name already exists" (3100) as non-fatal so callers
    #    (like add_vendor_list) can handle it gracefully.
    if status_code not in (0, 1, 3100):
        raise RuntimeError(f"QuickBooks Error {status_code}: {status_message}")

    return root


def fetch_vendor_list(company_file: str | None = None) -> List[Vendor]:
    qbxml = """<?xml version="1.0"?>
<?qbxml version="13.0"?>
<QBXML>
  <QBXMLMsgsRq onError="stopOnError">
    <VendorQueryRq/>
  </QBXMLMsgsRq>
</QBXML>"""

    root = _send_qbxml(qbxml)
    vendors: List[Vendor] = []

    for vend in root.findall(".//VendorRet"):
        name = (vend.findtext("Name") or "").strip()
        fax = (vend.findtext("Fax") or "").strip()
        if not fax:
            for acr in vend.findall("AdditionalContactRef"):
                cname = (acr.findtext("ContactName") or "").strip().lower()
                if cname == "fax":
                    fax = (acr.findtext("ContactValue") or "").strip()
                    if fax:
                        break
        if name or fax:
            vendors.append(Vendor(record_id=fax, name=name, source="quickbooks"))
    return vendors


def add_vendor_list(vendors: list[Vendor]) -> None:
    """Add or update vendors in QuickBooks in a single batch request."""

    if not vendors:
        print("No vendors to add.")
        return

    def xml_escape(text: str) -> str:
        """Escape special XML characters safely."""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;")
        )

    # Build each VendorAddRq block using the same multiline style
    # as your working VendorQueryRq request.
    vendor_add_rqs_lines: list[str] = []
    for vendor in vendors:
        name = xml_escape(vendor.name or "")
        fax = xml_escape(vendor.record_id or "")

        vendor_add_rqs_lines.append(
            '    <VendorAddRq requestID="{fax}">\n'
            "      <VendorAdd>\n"
            "        <Name>{name}</Name>\n"
            "        <IsActive>true</IsActive>\n"
            "        <Fax>{fax}</Fax>\n"
            "      </VendorAdd>\n"
            "    </VendorAddRq>".format(name=name, fax=fax)
        )

    vendor_add_rqs = "\n".join(vendor_add_rqs_lines)

    # IMPORTANT: Header now matches your working fetch_vendor_list() header
    qbxml = (
        '<?xml version="1.0"?>\n'
        '<?qbxml version="13.0"?>\n'
        "<QBXML>\n"
        '  <QBXMLMsgsRq onError="continueOnError">\n'
        f"{vendor_add_rqs}\n"
        "  </QBXMLMsgsRq>\n"
        "</QBXML>"
    )

    print("--- QBXML SENT ---")
    print(qbxml)

    root = _send_qbxml(qbxml)

    added = 0
    skipped_existing = 0

    for vend_resp in root.findall(".//VendorAddRs"):
        status_code = int(vend_resp.get("statusCode", "0"))
        status_message = vend_resp.get("statusMessage", "")

        if status_code == 0:
            added += 1
        elif status_code == 3100:
            skipped_existing += 1
            print(f"Vendor already exists in QuickBooks: {status_message}")
        else:
            print(f"Vendor add failed: {status_message}")

    print(f"{added} vendors successfully added to QuickBooks with Fax numbers.")
    if skipped_existing:
        print(
            f"{skipped_existing} vendors were skipped because they already "
            "exist in QuickBooks."
        )


# if __name__ == "__main__":
#     from .models import Vendor

#     # Example manual execution
#     test_vendors = [
#         Vendor(record_id="2001", name="Test Vendor A", source="excel"),
#         Vendor(record_id="2002", name="Test Vendor B", source="excel"),
#     ]

#     print("Attempting to add vendors to QuickBooks...")
#     add_vendor_list(test_vendors)
