from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
import pyperclip  # to access clipboard
import pyautogui  # to send Ctrl+A / Ctrl+C
import os
import sys # Import sys for command-line arguments

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
        filepath = os.path.join(os.getcwd(), "data", "raw", filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text_data)

        print(f"✅ Data copied and saved to {filepath}")
    except Exception as e:
        print(f"Error during scraping or saving: {e}")
        sys.stderr.write(f"An error occurred in exportersindia_dom_scraper for {company_name}: {str(e)}\n")
        sys.exit(1) # Exit with non-zero code to signal failure
    finally:
        driver.quit()

if __name__ == "__main__":
    # --- MODIFICATION: Get company name from command-line argument ---
    if len(sys.argv) < 2:
        print("Error: Company name required as argument.")
        sys.exit(1)
    company = sys.argv[1]
    print(f"Exporters India Scraper started for: {company}")
    # ----------------------------------------------------------------
    scrape_exportersindia(company)