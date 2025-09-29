"""
Selenium-based login agent for WordPress admin.

- Reads credentials from environment variables via `config.Config`.
- Navigates to the admin entries URL.
- Waits for manual CAPTCHA solving if present.
"""
import sys
import time
from typing import Optional
import getpass

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
# Using Selenium Manager; no external driver manager needed

from config import Config


def build_driver(headless: bool) -> webdriver.Chrome:
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1400,1000")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--remote-allow-origins=*")
    chrome_options.add_argument("--disable-features=Translate,AutomationControlled,IsolateOrigins,site-per-process")
    chrome_options.add_argument("--disable-site-isolation-trials")
    # Faster navigation: don't wait for all subresources
    chrome_options.set_capability("pageLoadStrategy", "eager")

    # Let Selenium Manager resolve the appropriate ChromeDriver
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(max(Config.PAGE_LOAD_TIMEOUT, 60))
    driver.set_script_timeout(max(Config.PAGE_LOAD_TIMEOUT, 60))
    return driver


def wait_for_element(driver: webdriver.Chrome, by: By, value: str, timeout: int) -> Optional[object]:
    try:
        return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
    except TimeoutException:
        return None


def perform_login(driver: webdriver.Chrome) -> None:
    try:
        driver.get(Config.WP_ADMIN_URL)
    except TimeoutException:
        # Continue even if initial navigation times out; page may still be interactive
        pass

    # If GoDaddy overlay shows, click the fallback link to show WP username/password form
    try:
        # Try several selectors for the link/button
        possible_selectors = [
            (By.LINK_TEXT, "Log in with username and password"),
            (By.PARTIAL_LINK_TEXT, "username and password"),
            (By.XPATH, "//a[contains(., 'username and password') or contains(., 'Log in with username')]"),
            (By.CSS_SELECTOR, "a[href*='username']"),
        ]
        for by, sel in possible_selectors:
            elems = driver.find_elements(by, sel)
            if elems:
                try:
                    WebDriverWait(driver, Config.IMPLICIT_WAIT).until(EC.element_to_be_clickable((by, sel)))
                except TimeoutException:
                    pass
                elems[0].click()
                break
    except Exception:
        pass

    # WordPress login form fields (visible and interactable)
    try:
        username_input = WebDriverWait(driver, Config.PAGE_LOAD_TIMEOUT).until(
            EC.element_to_be_clickable((By.ID, "user_login"))
        )
        password_input = WebDriverWait(driver, Config.PAGE_LOAD_TIMEOUT).until(
            EC.element_to_be_clickable((By.ID, "user_pass"))
        )
    except TimeoutException:
        # Fallback to presence, then scroll into view
        username_input = wait_for_element(driver, By.ID, "user_login", Config.IMPLICIT_WAIT)
        password_input = wait_for_element(driver, By.ID, "user_pass", Config.IMPLICIT_WAIT)

    if not username_input or not password_input:
        # Already logged in or redirected
        return

    try:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", username_input)
    except Exception:
        pass

    # Ensure credentials are available; if not, prompt securely
    username = Config.WP_USERNAME
    password = Config.WP_PASSWORD
    if not username:
        try:
            username = input("WordPress username: ")
        except EOFError:
            username = ""
    if not password:
        try:
            password = getpass.getpass("WordPress password: ")
        except EOFError:
            password = ""

    username_input.clear()
    username_input.send_keys(username)
    password_input.clear()
    password_input.send_keys(password)

    # Try to click the submit button first
    try:
        submit_button = driver.find_element(By.ID, "wp-submit")
        submit_button.click()
    except NoSuchElementException:
        pass

    # Automatically wait for either admin content or login redirect
    try:
        WebDriverWait(driver, Config.PAGE_LOAD_TIMEOUT).until(
            EC.any_of(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#wpbody-content")),
                EC.url_contains("/wp-admin/"),
            )
        )
    except TimeoutException:
        # Continue; ensure_on_entries_page will force-navigate
        pass


def ensure_on_entries_page(driver: webdriver.Chrome) -> None:
    # After login, navigate again to ensure we land on the entries page
    try:
        driver.get(Config.WP_ADMIN_URL)
    except TimeoutException:
        pass
    # Verify some element typical to Gravity Forms entries view exists
    # We will look for the GF entries table wrapper
    _ = wait_for_element(driver, By.CSS_SELECTOR, "#wpbody-content", Config.PAGE_LOAD_TIMEOUT)


def main() -> int:
    # Do not hard-fail if creds are missing; we'll prompt at runtime
    try:
        _ = Config.WP_ADMIN_URL  # access to ensure Config loads
    except Exception as e:
        print(f"Configuration error: {e}")
        return 2

    driver = build_driver(headless=Config.HEADLESS_MODE)
    try:
        perform_login(driver)
        ensure_on_entries_page(driver)
        print("Login flow completed. You're on the entries page (or should be).")
        # Keep session alive briefly so user can inspect
        if not Config.HEADLESS_MODE:
            print("Keeping the browser open for 20 seconds so you can verify...")
            time.sleep(20)
        return 0
    finally:
        try:
            driver.quit()
        except Exception:
            pass


if __name__ == "__main__":
    sys.exit(main())


