"""
Export a Gravity Forms entry by parsing the visible text content.

Flow:
- Login using env (WP_USERNAME/WP_PASSWORD) and open ENTRY_ID
- Save visible text from #wpbody-content
- Parse label/value pairs from consecutive lines
- Save to CSV and JSON with timestamp and entry id
"""
import csv
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Tuple

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from config import Config
from export_first_entry import open_entry_by_id
from login_agent import build_driver, perform_login


KNOWN_LABELS = {
    "Product",
    "Quantity",
    "Approval Confirmation",
    "Employee ID",
    "Site Number",
    "First Name",
    "Last Name",
    "Birthdate",
    "Phone",
    "Employee Email",
    "Signature",
    "Order Status",
}

SECTION_HEADERS = {
    "Employee Information",
    "Employee Contact Information",
}


def save_visible_text(driver) -> str:
    out_dir = os.path.dirname(os.path.abspath(__file__))
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    txt_path = os.path.join(out_dir, f"entry_visible_{ts}.txt")
    try:
        container = driver.find_element(By.CSS_SELECTOR, "#wpbody-content")
        text = container.text
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)
        return txt_path
    except Exception:
        return txt_path


def parse_text_lines(lines: List[str]) -> List[Tuple[str, str]]:
    pairs: List[Tuple[str, str]] = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        # Skip section headers
        if line in SECTION_HEADERS:
            i += 1
            continue
        # Colon form: Label: value
        if ":" in line:
            parts = line.split(":", 1)
            label = parts[0].strip()
            value = parts[1].strip()
            if label and value:
                pairs.append((label, value))
                i += 1
                continue
        # Known label followed by value on next non-empty line
        if line in KNOWN_LABELS and i + 1 < n:
            value = lines[i + 1].strip()
            if value:
                pairs.append((line, value))
                i += 2
                continue
        i += 1
    return pairs


def write_outputs(entry_id: str, pairs: List[Tuple[str, str]]) -> Tuple[str, str]:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = f"entry_{entry_id}_{timestamp}"
    out_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(out_dir, base + ".csv")
    json_path = os.path.join(out_dir, base + ".json")

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["label", "value"])
        for label, value in pairs:
            writer.writerow([label, value])

    obj: Dict[str, str] = {k: v for k, v in pairs}
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

    return csv_path, json_path


def main() -> int:
    entry_id = os.getenv("ENTRY_ID", "") or (sys.argv[1] if len(sys.argv) > 1 else "")
    if not entry_id:
        print("Provide ENTRY_ID env or as first CLI arg.")
        return 2

    driver = build_driver(headless=True)
    try:
        perform_login(driver)
        open_entry_by_id(driver, entry_id)
        try:
            WebDriverWait(driver, max(Config.PAGE_LOAD_TIMEOUT, 60)).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#wpbody-content"))
            )
        except TimeoutException:
            pass
        txt_path = save_visible_text(driver)
        with open(txt_path, "r", encoding="utf-8") as f:
            lines = [ln.rstrip("\n") for ln in f]
        pairs = parse_text_lines(lines)
        csv_path, json_path = write_outputs(entry_id, pairs)
        print(f"Saved text: {txt_path}")
        print(f"Wrote CSV: {csv_path}")
        print(f"Wrote JSON: {json_path}")
        return 0
    finally:
        try:
            driver.quit()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())


