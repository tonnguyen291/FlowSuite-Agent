"""
Automate login to NetSuite login page using Selenium.

- Reads NS_USERNAME/NS_PASSWORD from environment variables.
- Opens provided login URL (default: system login page).
- Waits for 2FA/redirect if present.
"""
import os
import sys
import time
from typing import Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from login_agent import build_driver


def wait_present(driver, locator: tuple, timeout: int) -> Optional[object]:
    try:
        return WebDriverWait(driver, timeout).until(EC.presence_of_element_located(locator))
    except TimeoutException:
        return None


def wait_clickable(driver, locator: tuple, timeout: int) -> Optional[object]:
    try:
        return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(locator))
    except TimeoutException:
        return None


def perform_netsuite_login(driver, login_url: str, username: str, password: str) -> None:
    try:
        driver.get(login_url)
    except TimeoutException:
        pass

    # Try common selectors for NetSuite login page
    email_el = (
        wait_present(driver, (By.ID, "email"), 20)
        or wait_present(driver, (By.NAME, "email"), 5)
        or wait_present(driver, (By.CSS_SELECTOR, "input[type='email']"), 5)
    )
    password_el = (
        wait_present(driver, (By.ID, "password"), 20)
        or wait_present(driver, (By.NAME, "password"), 5)
        or wait_present(driver, (By.CSS_SELECTOR, "input[type='password']"), 5)
    )

    if email_el and password_el:
        try:
            email_el.clear()
        except Exception:
            pass
        email_el.send_keys(username)
        try:
            password_el.clear()
        except Exception:
            pass
        password_el.send_keys(password)

        # Click Login
        login_btn = (
            wait_clickable(driver, (By.ID, "login-submit"), 10)
            or wait_clickable(driver, (By.CSS_SELECTOR, "button[type='submit']"), 5)
            or wait_clickable(driver, (By.XPATH, "//button[contains(., 'Log In') or contains(., 'Sign In')]"), 5)
        )
        if login_btn:
            login_btn.click()

    # Wait for potential 2FA or redirect after credentials
    try:
        WebDriverWait(driver, 120).until(
            EC.any_of(
                EC.url_contains("app.netsuite.com/app/center"),
                EC.presence_of_element_located((By.CSS_SELECTOR, "#ns-navigation-container, #ns-header, #ns-sidebar")),
                EC.presence_of_element_located((By.ID, "multifactor")),
                EC.presence_of_element_located((By.ID, "twoFactorAuth")),
            )
        )
    except TimeoutException:
        pass


def main() -> int:
    login_url = os.getenv("NS_LOGIN_URL", "https://system.netsuite.com/pages/customerlogin.jsp?country=US")
    username = os.getenv("NS_USERNAME", "") or (sys.argv[1] if len(sys.argv) > 1 else "")
    password = os.getenv("NS_PASSWORD", "") or (sys.argv[2] if len(sys.argv) > 2 else "")
    if not username or not password:
        print("Missing NS_USERNAME/NS_PASSWORD. Provide via env or CLI args.")
        return 2

    # Force visible browser to allow 2FA interaction
    os.environ["HEADLESS_MODE"] = "False"
    driver = build_driver(headless=False)
    try:
        perform_netsuite_login(driver, login_url, username, password)
        # Keep open a bit for manual 2FA/role selection if needed
        print("Login attempted. Leaving browser open for 60 seconds for 2FA/verification...")
        time.sleep(60)
        return 0
    finally:
        try:
            driver.quit()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())


