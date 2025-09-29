"""
Export Gravity Forms entry fields as CSV and JSON.

Modes:
- Default: export the first entry on the list
- Specific: export a specific entry by ID via CLI arg --entry-id or env ENTRY_ID

Steps:
- Launch Chrome via Selenium (same options as login_agent)
- Log in using env vars (or runtime prompt fallback via login_agent)
- Navigate to target entry view
- Scrape field label/value pairs
- Write CSV (two columns: label,value) and JSON (object)
"""
import csv
import json
import os
import sys
import urllib.parse
from datetime import datetime
from typing import Dict, List, Tuple

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from config import Config
from login_agent import build_driver, wait_for_element, perform_login, ensure_on_entries_page


def click_first_entry(driver) -> None:
    # Try common selectors for GF "View" link
    selectors = [
        (By.CSS_SELECTOR, "a[href*='view=entry']"),
        (By.XPATH, "//a[contains(@href,'view=entry')]"),
        (By.CSS_SELECTOR, "table tbody tr:first-child a"),
        (By.XPATH, "(//table//tbody//tr//a)[1]"),
    ]
    for by, sel in selectors:
        try:
            WebDriverWait(driver, Config.PAGE_LOAD_TIMEOUT).until(
                EC.presence_of_element_located((by, sel))
            )
            links = driver.find_elements(by, sel)
            if links:
                try:
                    WebDriverWait(driver, Config.IMPLICIT_WAIT).until(EC.element_to_be_clickable((by, sel)))
                except TimeoutException:
                    pass
                links[0].click()
                return
        except TimeoutException:
            continue
    raise RuntimeError("Could not find an entry to view.")


def get_form_id_from_admin_url(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    qs = urllib.parse.parse_qs(parsed.query)
    form_ids = qs.get("id") or qs.get("form_id") or []
    if not form_ids:
        raise ValueError("Could not determine form id from admin URL")
    return str(form_ids[0])


def open_entry_by_id(driver, entry_id: str) -> None:
    form_id = get_form_id_from_admin_url(Config.WP_ADMIN_URL)
    # Gravity Forms entry view URL pattern
    entry_url = f"https://dtcrxoptics.com/wp-admin/admin.php?page=gf_entries&view=entry&id={form_id}&lid={entry_id}"
    try:
        driver.get(entry_url)
    except TimeoutException:
        pass
    try:
        WebDriverWait(driver, Config.PAGE_LOAD_TIMEOUT).until(
            EC.any_of(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#wpbody-content")),
                EC.url_contains("view=entry"),
            )
        )
    except TimeoutException:
        pass


def save_current_html(driver, entry_id: str) -> str:
    out_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(out_dir, f"entry_{entry_id}_raw.html")
    try:
        html = driver.page_source
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
    except Exception:
        pass
    return path


def scrape_entry_fields(driver) -> List[Tuple[str, str]]:
    # Wait for entry view page to load
    try:
        WebDriverWait(driver, Config.PAGE_LOAD_TIMEOUT).until(
            EC.any_of(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table")),
                EC.presence_of_element_located((By.CSS_SELECTOR, "dl")),
                EC.url_contains("view=entry"),
            )
        )
    except TimeoutException:
        pass

    pairs: List[Tuple[str, str]] = []

    # Pattern 1: table rows with th/td
    try:
        rows = driver.find_elements(By.CSS_SELECTOR, "table tr")
        for row in rows:
            try:
                label_el = row.find_element(By.CSS_SELECTOR, "th, td.label, td.column-label")
                value_el = row.find_element(By.CSS_SELECTOR, "td:not(.label):not(.column-label)")
                label = label_el.text.strip()
                value = value_el.text.strip()
                if label and value:
                    pairs.append((label, value))
            except Exception:
                continue
    except Exception:
        pass

    # Pattern 2: dl dt/dd
    if not pairs:
        try:
            dts = driver.find_elements(By.CSS_SELECTOR, "dl dt")
            for dt in dts:
                label = dt.text.strip()
                try:
                    dd = dt.find_element(By.XPATH, "following-sibling::dd[1]")
                    value = dd.text.strip()
                except NoSuchElementException:
                    value = ""
                if label and value:
                    pairs.append((label, value))
        except Exception:
            pass

    # Fallback: collect key/value rows where there are two tds
    if not pairs:
        try:
            rows = driver.find_elements(By.CSS_SELECTOR, "table tr")
            for row in rows:
                tds = row.find_elements(By.TAG_NAME, "td")
                if len(tds) >= 2:
                    label = tds[0].text.strip()
                    value = tds[1].text.strip()
                    if label and value:
                        pairs.append((label, value))
        except Exception:
            pass

    return pairs


def write_outputs(pairs: List[Tuple[str, str]]) -> Tuple[str, str]:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = f"first_entry_{timestamp}"
    out_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(out_dir, base + ".csv")
    json_path = os.path.join(out_dir, base + ".json")

    # CSV
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["label", "value"])
        for label, value in pairs:
            writer.writerow([label, value])

    # JSON
    obj: Dict[str, str] = {label: value for label, value in pairs}
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

    return csv_path, json_path


def main() -> int:
    # Resolve optional entry id: CLI arg --entry-id or env ENTRY_ID
    entry_id: str = ""
    for i, arg in enumerate(sys.argv):
        if arg == "--entry-id" and i + 1 < len(sys.argv):
            entry_id = sys.argv[i + 1]
            break
    if not entry_id:
        entry_id = os.getenv("ENTRY_ID", "")

    driver = build_driver(headless=Config.HEADLESS_MODE)
    try:
        perform_login(driver)
        ensure_on_entries_page(driver)
        if entry_id:
            open_entry_by_id(driver, entry_id)
            saved_path = save_current_html(driver, entry_id)
        else:
            click_first_entry(driver)
        pairs = scrape_entry_fields(driver)
        if not pairs:
            print("No fields found on the first entry page.")
        if entry_id:
            print(f"Saved raw HTML for entry {entry_id} to: {saved_path}")
        csv_path, json_path = write_outputs(pairs)
        print(f"Wrote CSV: {csv_path}")
        print(f"Wrote JSON: {json_path}")
        return 0
    finally:
        try:
            driver.quit()
        except Exception:
            pass


if __name__ == "__main__":
    sys.exit(main())


