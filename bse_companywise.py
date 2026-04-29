from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import sys
import pyautogui
import pyperclip

# Use company name passed from orchestrator
company_name = sys.argv[1] if len(sys.argv) > 1 else "DefaultCompany"

# === Step 1: Setup Selenium ===
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

# === Step 2: Open BSE website ===
driver.get("https://www.bseindia.com/markets/equity/EQReports/MarketWatch.html?index_code=17")

# === Step 3: Search for company ===

search_box = driver.find_element(By.ID, "getquotesearch")
search_box.send_keys(company_name)
time.sleep(2)  # wait for suggestions to appear

# Click the first result
first_result = driver.find_element(By.CSS_SELECTOR, "li.quotemenu")
first_result.click()
time.sleep(3)

# === Step 4: Scroll to and click Financials ===
financials_tab = driver.find_element(By.ID, "afi")
driver.execute_script("arguments[0].scrollIntoView(true);", financials_tab)
time.sleep(1)  # allow rendering
financials_tab.click()
time.sleep(2)

# === Step 5: Click Results ===
results_link = driver.find_element(By.ID, "l61")
driver.execute_script("arguments[0].scrollIntoView(true);", results_link)
time.sleep(1)
results_link.click()
time.sleep(3)

# === Step 6: Click "click here" hyperlink ===
click_here_link = driver.find_element(By.LINK_TEXT, "click here.")
driver.execute_script("arguments[0].scrollIntoView(true);", click_here_link)
time.sleep(1)
click_here_link.click()
time.sleep(3)

# Switch to new window
driver.switch_to.window(driver.window_handles[-1])
time.sleep(2)

# === Step 7: Click XBRL link ===
xbrl_link = driver.find_element(By.CSS_SELECTOR, "a.fa-file-code-o")
driver.execute_script("arguments[0].scrollIntoView(true);", xbrl_link)
time.sleep(1)  # allow rendering
xbrl_link.click()
time.sleep(3)

# Switch to new XBRL window
driver.switch_to.window(driver.window_handles[-1])
time.sleep(2)

# === Step 8: Copy all XBRL page content using Ctrl+A + Ctrl+C ===
try:
    # Focus on the page
    body = driver.find_element(By.TAG_NAME, "body")
    body.click()
    time.sleep(1)
    
    # Select all text
    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.5)
    
    # Copy to clipboard
    pyautogui.hotkey("ctrl", "c")
    time.sleep(1)
    
    # Get text from clipboard
    page_content = pyperclip.paste()
    
    # Save to TXT file
    with open(f"{company_name}_xbrl.txt", "w", encoding="utf-8") as f:
        f.write(page_content)
    
    print(f"✅ XBRL content copied via clipboard and saved for {company_name}")

except Exception as e:
    print(f"❌ Failed to copy XBRL content: {e}")



# === Step 10: Close the browser ===
driver.quit()
