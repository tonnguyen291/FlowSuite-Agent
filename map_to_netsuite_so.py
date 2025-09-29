"""
Map exported entry JSON to a minimal NetSuite Sales Order CSV.

Columns (example):
- Entity: customer identifier (email or name)
- Item: product name
- Quantity: numeric quantity
- Memo: concatenated details (site, employee id, phone, etc.)
"""
import csv
import json
import os
import sys
from datetime import datetime


def load_entry_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def map_to_so_rows(entry: dict) -> list[dict]:
    # Extract fields with fallbacks
    product = entry.get("Product") or entry.get("product") or "Unknown Item"
    quantity = entry.get("Quantity") or entry.get("quantity") or "1"
    email = entry.get("Employee Email") or entry.get("email") or ""
    first_name = entry.get("First Name") or ""
    last_name = entry.get("Last Name") or ""
    phone = entry.get("Phone") or ""
    employee_id = entry.get("Employee ID") or ""
    site_number = entry.get("Site Number") or ""
    entry_id = entry.get("Entry Id") or entry.get("entryId") or ""
    form_name = entry.get("DT IMAGE RX Checkout (No RX)") or entry.get("form") or ""

    # Entity preference: email, else full name
    entity = email if email else (f"{first_name} {last_name}".strip() or "Unknown Customer")

    memo_parts = []
    if form_name:
        memo_parts.append(f"Form: {form_name}")
    if entry_id:
        memo_parts.append(f"Entry: {entry_id}")
    if employee_id:
        memo_parts.append(f"Employee ID: {employee_id}")
    if site_number:
        memo_parts.append(f"Site: {site_number}")
    if phone:
        memo_parts.append(f"Phone: {phone}")
    memo = " | ".join(memo_parts)

    try:
        qty_str = str(quantity).strip()
        # Keep as string in CSV; NetSuite will parse
    except Exception:
        qty_str = "1"

    return [{
        "Entity": entity,
        "Item": product,
        "Quantity": qty_str,
        "Memo": memo,
    }]


def write_csv(rows: list[dict], out_path: str) -> None:
    fieldnames = ["Entity", "Item", "Quantity", "Memo"]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python map_to_netsuite_so.py /path/to/entry_<id>_*.json")
        return 2
    in_path = sys.argv[1]
    if not os.path.exists(in_path):
        print(f"File not found: {in_path}")
        return 2
    entry = load_entry_json(in_path)
    rows = map_to_so_rows(entry)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    entry_id = entry.get("Entry Id") or "unknown"
    out_dir = os.path.dirname(os.path.abspath(in_path))
    out_path = os.path.join(out_dir, f"netsuite_sales_order_{entry_id}_{ts}.csv")
    write_csv(rows, out_path)
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


