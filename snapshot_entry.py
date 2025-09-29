import os
import sys
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from config import Config
from export_first_entry import open_entry_by_id
from login_agent import build_driver, perform_login


def main() -> int:
    entry_id = os.getenv("ENTRY_ID", "") or (sys.argv[1] if len(sys.argv) > 1 else "")
    if not entry_id:
        print("Provide ENTRY_ID env or as first CLI arg.")
        return 2

    driver = build_driver(headless=True)
    try:
        perform_login(driver)
        open_entry_by_id(driver, entry_id)

        # Wait for content area
        try:
            WebDriverWait(driver, max(Config.PAGE_LOAD_TIMEOUT, 60)).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#wpbody-content"))
            )
        except TimeoutException:
            pass

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_dir = os.path.dirname(os.path.abspath(__file__))
        png_path = os.path.join(out_dir, f"entry_{entry_id}_{ts}.png")
        txt_path = os.path.join(out_dir, f"entry_{entry_id}_{ts}.txt")

        # Screenshot
        try:
            driver.save_screenshot(png_path)
        except Exception:
            pass

        # Visible text
        try:
            container = driver.find_element(By.CSS_SELECTOR, "#wpbody-content")
            text = container.text
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(text)
        except Exception:
            pass

        print(f"Saved screenshot: {png_path}")
        print(f"Saved text dump: {txt_path}")
        return 0
    finally:
        try:
            driver.quit()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())


