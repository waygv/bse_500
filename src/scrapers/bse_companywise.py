from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import sys
import pyautogui
import pyperclip

# === HARDCODED COMPANY NAME ===
TARGET_COMPANY = "CIPLA"  # <--- CHANGE THIS TO YOUR TARGET COMPANY

# Use hardcoded name or fall back to sys.argv
company_name = TARGET_COMPANY or (sys.argv[1] if len(sys.argv) > 1 else "DefaultCompany")

# Get project root (2 levels up from src/scrapers/)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
os.makedirs(DATA_RAW_DIR, exist_ok=True)

# === Step 1: Setup Selenium ===
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

# === Step 2: Open BSE Home (better for search) ===
driver.get("https://beta.bseindia.com/stock-share-price/lupin-ltd/lupin/500257/")

try:
    wait = WebDriverWait(driver, 20)
    
    # === Step 3: Search for company ===
    # FIXED: presence_of_element_located instead of presence_of_element_status
    search_box = wait.until(EC.presence_of_element_located((By.ID, "getquotesearch")))
    search_box.clear()
    search_box.send_keys(company_name)
    time.sleep(3)  # wait for suggestions to appear

    # Click the first result
    first_result = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "li.quotemenu")))
    first_result.click()
    time.sleep(5)

    # === Step 4: Scroll to and click Financials ===
    financials_tab = wait.until(EC.presence_of_element_located((By.ID, "afi")))
    driver.execute_script("arguments[0].scrollIntoView(true);", financials_tab)
    time.sleep(2)
    financials_tab.click()
    time.sleep(3)

    # === Step 5: Click Results ===
    results_link = wait.until(EC.element_to_be_clickable((By.ID, "l61")))
    driver.execute_script("arguments[0].scrollIntoView(true);", results_link)
    time.sleep(2)
    results_link.click()
    time.sleep(3)

    # === Step 6: Click "click here" hyperlink ===
    click_here_link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "click here.")))
    driver.execute_script("arguments[0].scrollIntoView(true);", click_here_link)
    time.sleep(2)
    click_here_link.click()
    time.sleep(3)

    # Switch to new window
    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(2)

    # === Step 7: Click XBRL link ===
    xbrl_link = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.fa-file-code-o")))
    driver.execute_script("arguments[0].scrollIntoView(true);", xbrl_link)
    time.sleep(2)
    xbrl_link.click()
    time.sleep(3)

    # Switch to new XBRL window
    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(2)

    # === Step 8: Copy all XBRL page content using Ctrl+A + Ctrl+C ===
    body = driver.find_element(By.TAG_NAME, "body")
    body.click()
    time.sleep(2)
    
    pyautogui.hotkey("ctrl", "a")
    time.sleep(1)
    pyautogui.hotkey("ctrl", "c")
    time.sleep(1)
    
    page_content = pyperclip.paste()
    
    filepath = os.path.join(DATA_RAW_DIR, f"{company_name}_xbrl.txt")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(page_content)
    
    print(f"SUCCESS: XBRL content saved for {company_name} to {filepath}")

except Exception as e:
    print(f"ERROR: Error occurred in bse_companywise: {e}")

finally:
    driver.quit()
