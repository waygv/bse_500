from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

# Get project root
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

def scrape_bse_industry():
    """Trigger Selenium to download the Index.csv from BSE with robust headers."""
    os.makedirs(DATA_PROCESSED_DIR, exist_ok=True)
    
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

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
        
        print("Waiting for Index.csv download...")
        time.sleep(15) 
        
        return f"SUCCESS: Index download triggered to {DATA_PROCESSED_DIR}"
    except Exception as e:
        return f"ERROR: Index download failed: {str(e)}"
    finally:
        driver.quit()

if __name__ == "__main__":
    print(scrape_bse_industry())
