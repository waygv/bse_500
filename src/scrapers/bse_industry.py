from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import glob

# Get project root
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

def scrape_bse_industry():
    """Trigger Stealth Selenium to download Index.csv and ensure clean naming."""
    print(f"SCRAPER: Starting Index download to {DATA_PROCESSED_DIR}...")
    os.makedirs(DATA_PROCESSED_DIR, exist_ok=True)
    
    target_filename = "Index.csv"
    target_path = os.path.join(DATA_PROCESSED_DIR, target_filename)

    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")

    prefs = {
        "download.default_directory": DATA_PROCESSED_DIR,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)

    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    url = "https://www.bseindia.com/sensex/IndexHighlight.html"
    
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 30)
        
        download_icon = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "i.fa.fa-download.iconfont"))
        )
        driver.execute_script("arguments[0].click();", download_icon)
        
        print("SCRAPER: Index download clicked. Waiting...")
        time.sleep(15) 
        
        # --- SMART RENAMING ---
        all_files = glob.glob(os.path.join(DATA_PROCESSED_DIR, "*"))
        csv_files = [f for f in all_files if (".csv" in f or "Index" in f) and target_filename not in os.path.basename(f)]
        
        if csv_files:
            latest_download = max(csv_files, key=os.path.getmtime)
            if os.path.exists(target_path): os.remove(target_path)
            os.rename(latest_download, target_path)
            print(f"SCRAPER: Successfully saved fresh {target_filename}")
        else:
            print(f"SCRAPER: No new file found to rename for {target_filename}.")

        return "SUCCESS"
    except Exception as e:
        print(f"SCRAPER ERROR: Index failed: {str(e)}")
        return f"ERROR: {str(e)}"
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_bse_industry()
