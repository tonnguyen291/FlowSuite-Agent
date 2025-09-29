"""
Create a NetSuite Sales Order from an exported entry JSON.

Behavior:
- Logs in to NetSuite using NS_USERNAME/NS_PASSWORD/NS_LOGIN_URL env vars (visible browser)
- Navigates to Sales Order creation page
- Attempts to populate Entity, Item, Quantity, and Memo
- Leaves browser open for manual verification and Save

Notes:
- NetSuite UIs vary by account/role. This script tries common selectors, then shows values for manual paste if needed.
"""
import os
import sys
import json
import time
from typing import Dict

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from login_agent import build_driver
from netsuite_login import perform_netsuite_login


NS_SO_URL = "https://system.netsuite.com/app/accounting/transactions/salesord.nl?whence="


def load_entry(path: str) -> Dict[str, str]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def map_entry(entry: Dict[str, str]) -> Dict[str, str]:
    product = entry.get("Product") or entry.get("product") or "Unknown Item"
    quantity = str(entry.get("Quantity") or entry.get("quantity") or "1")
    email = entry.get("Employee Email") or entry.get("email") or ""
    first_name = entry.get("First Name") or ""
    last_name = entry.get("Last Name") or ""
    entity = email if email else (f"{first_name} {last_name}".strip() or "Unknown Customer")
    employee_id = entry.get("Employee ID") or ""
    site_number = entry.get("Site Number") or ""
    entry_id = entry.get("Entry Id") or entry.get("entryId") or ""
    form_name = entry.get("DT IMAGE RX Checkout (No RX)") or entry.get("form") or ""

    memo_parts = []
    if form_name:
        memo_parts.append(f"Form: {form_name}")
    if entry_id:
        memo_parts.append(f"Entry: {entry_id}")
    if employee_id:
        memo_parts.append(f"Employee ID: {employee_id}")
    if site_number:
        memo_parts.append(f"Site: {site_number}")
    memo = " | ".join(memo_parts)

    return {
        "entity": entity,
        "item": product,
        "quantity": quantity,
        "memo": memo,
    }


def safe_type(el, text: str) -> None:
    try:
        el.clear()
    except Exception:
        pass
    el.send_keys(text)


def try_fill_sales_order(driver, mapped: Dict[str, str]) -> None:
    # Wait for SO form
    try:
        WebDriverWait(driver, 60).until(
            EC.any_of(
                EC.presence_of_element_located((By.ID, "main_form")),
                EC.presence_of_element_located((By.CSS_SELECTOR, "form#main_form, form[name='main_form']")),
            )
        )
    except TimeoutException:
        pass

    # Entity field
    for locator in [
        (By.ID, "entityname"),
        (By.CSS_SELECTOR, "input[name='entity_display']"),
        (By.CSS_SELECTOR, "input#entityname_display, input#entityname, input[name='entityname']"),
    ]:
        els = driver.find_elements(*locator)
        if els:
            safe_type(els[0], mapped["entity"]) 
            break

    # Memo field
    for locator in [
        (By.ID, "memo"),
        (By.CSS_SELECTOR, "textarea#memo, textarea[name='memo']"),
    ]:
        els = driver.find_elements(*locator)
        if els:
            safe_type(els[0], mapped["memo"]) 
            break

    # Add item row
    # Click "Add" on item sublist if present
    try:
        add_btn = (
            WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.ID, "item_addedit")))
            or WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input#item_addedit, button#item_addedit")))
        )
    except Exception:
        add_btn = None

    # Item name field on sublist
    item_field = None
    for locator in [
        (By.ID, "item_display"),
        (By.CSS_SELECTOR, "input#item_display, input[name='item_display']"),
        (By.ID, "inpt_item"),
    ]:
        els = driver.find_elements(*locator)
        if els:
            item_field = els[0]
            break
    if item_field:
        safe_type(item_field, mapped["item"]) 

    # Quantity field
    qty_field = None
    for locator in [
        (By.ID, "quantity_formattedValue"),
        (By.CSS_SELECTOR, "input#quantity, input#quantity_formattedValue"),
        (By.NAME, "quantity"),
    ]:
        els = driver.find_elements(*locator)
        if els:
            qty_field = els[0]
            break
    if qty_field:
        safe_type(qty_field, mapped["quantity"]) 

    if add_btn:
        try:
            add_btn.click()
        except Exception:
            pass


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python netsuite_create_so.py /path/to/entry_<id>_...json")
        return 2
    entry_json = sys.argv[1]
    if not os.path.exists(entry_json):
        print(f"File not found: {entry_json}")
        return 2
    entry = load_entry(entry_json)
    mapped = map_entry(entry)

    username = os.getenv("NS_USERNAME", "")
    password = os.getenv("NS_PASSWORD", "")
    login_url = os.getenv("NS_LOGIN_URL", "https://system.netsuite.com/pages/customerlogin.jsp?country=US")
    if not username or not password:
        print("Set NS_USERNAME and NS_PASSWORD env vars.")
        return 2

    # Visible browser for manual assistance
    os.environ["HEADLESS_MODE"] = "False"
    driver = build_driver(headless=False)
    try:
        perform_netsuite_login(driver, login_url, username, password)
        # Navigate directly to Sales Order page (NetSuite will route per role)
        try:
            driver.get(NS_SO_URL)
        except TimeoutException:
            pass

        try_fill_sales_order(driver, mapped)

        print("Filled values (paste if needed):")
        print(f"- Entity: {mapped['entity']}")
        print(f"- Item: {mapped['item']}")
        print(f"- Quantity: {mapped['quantity']}")
        print(f"- Memo: {mapped['memo']}")
        print("Leaving browser open for 90 seconds. Please review and click Save in NetSuite.")
        time.sleep(90)
        return 0
    finally:
        try:
            driver.quit()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())


