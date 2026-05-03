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
    """Deeply stealthy scraper to avoid blank screens and bot detection."""
    os.makedirs(DATA_RAW_DIR, exist_ok=True)
    
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=options)
    
    # Hide webdriver flag more deeply
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })

    filepath = os.path.join(DATA_RAW_DIR, f"{company_name.upper()}_xbrl.txt")

    try:
        # Start at a neutral page
        driver.get("https://www.google.com")
        time.sleep(2)
        
        # Navigate to BSE
        driver.get("https://www.bseindia.com/")
        wait = WebDriverWait(driver, 30)
        
        # Look for search box
        search_box = wait.until(EC.presence_of_element_located((By.ID, "getquotesearch")))
        search_box.click()
        search_box.send_keys(company_name)
        time.sleep(5)

        first_result = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "li.quotemenu")))
        first_result.click()
        
        # Financials
        wait.until(EC.presence_of_element_located((By.ID, "afi"))) 
        driver.execute_script("document.getElementById('afi').click();")
        time.sleep(3)

        # Results
        res_link = wait.until(EC.element_to_be_clickable((By.ID, "l61")))
        driver.execute_script("arguments[0].click();", res_link)
        time.sleep(3)

        # Click here
        click_here = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "click here.")))
        click_here.click()
        time.sleep(5)

        if len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[-1])
        
        # XBRL
        xbrl_link = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.fa-file-code-o")))
        xbrl_link.click()
        time.sleep(5)

        if len(driver.window_handles) > 2:
            driver.switch_to.window(driver.window_handles[-1])
        
        # Extract body text
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
    print(scrape_bse_xbrl("CIPLA"))
