from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import sys

# Get project root
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_RAW_DIR = os.path.join(BASE_DIR, "data", "raw")

def scrape_exportersindia(company_name: str):
    """Function to trigger Selenium and scrape ExportersIndia data using robust body.text extraction."""
    os.makedirs(DATA_RAW_DIR, exist_ok=True)
    
    query = company_name.replace(" ", "+")
    url = f"https://www.exportersindia.com/search.php?srch_catg_ty=comp&term={query}&cont=IN&ss_status=N"

    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(options=options)
    filepath = os.path.join(DATA_RAW_DIR, f"{company_name.replace(' ', '_').upper()}_exportersindia.txt")

    try:
        driver.get(url)
        wait = WebDriverWait(driver, 30)
        
        # Wait for body to be present
        body = wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(5) # Allow dynamic content to load

        # Extraction via .text is much more stable than clipboard
        text_data = body.text

        if not text_data or len(text_data) < 100:
             text_data = driver.page_source

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text_data)

        return f"SUCCESS: ExportersIndia data ({len(text_data)} chars) saved to {filepath}"
    except Exception as e:
        return f"ERROR: Scraper failed: {str(e)}"
    finally:
        driver.quit()

if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "CIPLA"
    print(scrape_exportersindia(name))
