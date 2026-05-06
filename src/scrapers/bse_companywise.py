from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
import os
import sys

# Get project root
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_RAW_DIR = os.path.join(BASE_DIR, "data", "raw")

def scrape_bse_xbrl(company_name: str):
    """Deeply stealthy scraper using the Beta site with robust click handling."""
    os.makedirs(DATA_RAW_DIR, exist_ok=True)
    
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=options)
    
    # Hide webdriver flag
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })

    filepath = os.path.join(DATA_RAW_DIR, f"{company_name.upper()}_xbrl.txt")

    try:
        # Use the Beta site as the entry point as suggested by user
        # This page usually has a search bar in the header
        driver.get("https://beta.bseindia.com/stock-share-price/lupin-ltd/lupin/500257/")
        wait = WebDriverWait(driver, 30)
        
        # Robust Search Box Interaction
        search_box = wait.until(EC.presence_of_element_located((By.ID, "getquotesearch")))
        
        # Scroll to it first to avoid "not clickable at point" errors
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", search_box)
        time.sleep(2)
        
        # Use JS to click and clear to bypass interceptors
        driver.execute_script("arguments[0].click();", search_box)
        driver.execute_script("arguments[0].value = '';", search_box)
        
        # Send keys
        search_box.send_keys(company_name)
        print(f"DEBUG: Searching for {company_name}...")
        time.sleep(5) # Wait for dropdown

        # Click the first result in the dropdown
        first_result = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "li.quotemenu")))
        driver.execute_script("arguments[0].click();", first_result)
        
        # --- Navigation to XBRL ---
        # Wait for the target company page to load (look for the 'afi' tab)
        wait.until(EC.presence_of_element_located((By.ID, "afi"))) 
        time.sleep(2)

        # Click Financials (using JS for stability)
        driver.execute_script("document.getElementById('afi').click();")
        time.sleep(3)

        # Click Results (l61)
        res_link = wait.until(EC.presence_of_element_located((By.ID, "l61")))
        driver.execute_script("arguments[0].click();", res_link)
        time.sleep(3)

        # Click "click here." link
        click_here = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "click here.")))
        driver.execute_script("arguments[0].click();", click_here)
        time.sleep(5)

        # Handle Windows
        if len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[-1])
        
        # XBRL Icon (fa-file-code-o)
        xbrl_link = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.fa-file-code-o")))
        driver.execute_script("arguments[0].click();", xbrl_link)
        time.sleep(5)

        if len(driver.window_handles) > 2:
            driver.switch_to.window(driver.window_handles[-1])
        
        # Extract Body Text
        body_text = wait.until(EC.presence_of_element_located((By.TAG_NAME, "body"))).text
        
        if not body_text or len(body_text) < 100:
             body_text = driver.page_source

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(body_text)
        
        return f"SUCCESS: Scraped {len(body_text)} characters for {company_name}"

    except Exception as e:
        return f"ERROR: Scraper failed: {str(e)}"

    finally:
        driver.quit()

if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "CIPLA"
    print(scrape_bse_xbrl(name))
