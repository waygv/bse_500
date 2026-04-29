from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
import pyperclip  # to access clipboard
import pyautogui  # to send Ctrl+A / Ctrl+C
import os
import sys

# === HARDCODED COMPANY NAME ===
TARGET_COMPANY = "CIPLA"  # <--- CHANGE THIS TO YOUR TARGET COMPANY

# Get project root (2 levels up from src/scrapers/)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
os.makedirs(DATA_RAW_DIR, exist_ok=True)

def scrape_exportersindia(company_name):
    # Replace spaces with '+'
    query = company_name.replace(" ", "+")
    url = f"https://www.exportersindia.com/search.php?srch_catg_ty=comp&term={query}&cont=IN&ss_status=N"

    # Configure Chrome options
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")

    service = Service()
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    time.sleep(5)  # wait for page to load

    # Focus the body and select + copy all text
    try:
        body = driver.find_element(By.TAG_NAME, "body")
        body.click()
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(1)
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(1)

        # Retrieve copied text
        text_data = pyperclip.paste()

        # Save to .txt file
        filename = f"{company_name.replace(' ', '_')}_exportersindia.txt"
        filepath = os.path.join(DATA_RAW_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text_data)

        print(f"SUCCESS: Data saved to {filepath}")
    except Exception as e:
        print(f"ERROR: Error during scraping or saving: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    # Use hardcoded name or fall back to sys.argv
    company = TARGET_COMPANY or (sys.argv[1] if len(sys.argv) > 1 else "DefaultCompany")
    print(f"START: Exporters India Scraper started for: {company}")
    scrape_exportersindia(company)
