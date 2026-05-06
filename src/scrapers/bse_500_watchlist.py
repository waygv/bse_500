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

def scrape_bse_500_watchlist():
    """Trigger Stealth Selenium to download MarketWatch.csv and ensure clean naming."""
    print(f"SCRAPER: Starting MarketWatch download to {DATA_PROCESSED_DIR}...")
    os.makedirs(DATA_PROCESSED_DIR, exist_ok=True)
    
    # Target filename
    target_filename = "MarketWatch.csv"
    target_path = os.path.join(DATA_PROCESSED_DIR, target_filename)

    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")

    prefs = {
        "download.default_directory": DATA_PROCESSED_DIR,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", prefs)

    service = Service()
    driver = webdriver.Chrome(service=service, options=options)
    
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })

    try:
        driver.get("https://www.google.com")
        time.sleep(2)
        
        url = "https://www.bseindia.com/markets/equity/EQReports/MarketWatch.html?index_code=17"
        driver.get(url)
        wait = WebDriverWait(driver, 30)
        
        download_icon = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "i.fa.fa-download.iconfont"))
        )
        driver.execute_script("arguments[0].click();", download_icon)
        
        print("SCRAPER: MarketWatch download clicked. Waiting...")
        time.sleep(15) 

        # --- SMART RENAMING ---
        # Look for files that ARE NOT our target but were just created
        all_files = glob.glob(os.path.join(DATA_PROCESSED_DIR, "*"))
        csv_files = [f for f in all_files if (".csv" in f or "MarketWatch" in f) and target_filename not in os.path.basename(f)]
        
        if csv_files:
            latest_download = max(csv_files, key=os.path.getmtime)
            if os.path.exists(target_path): os.remove(target_path)
            os.rename(latest_download, target_path)
            print(f"SCRAPER: Successfully saved fresh {target_filename}")
        else:
            print(f"SCRAPER: No new file found to rename for {target_filename}. Check if download started.")
        
        return "SUCCESS"
    except Exception as e:
        print(f"SCRAPER ERROR: MarketWatch failed: {str(e)}")
        return f"ERROR: {str(e)}"
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_bse_500_watchlist()
