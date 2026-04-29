from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

# Get project root (2 levels up from src/scrapers/)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(DATA_PROCESSED_DIR, exist_ok=True)

chrome_options = Options()
#chrome_options.add_argument("--headless")  
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

# === Set up download directory ===
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
driver.get(url)

try:
    wait = WebDriverWait(driver, 20)
    download_icon = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "i.fa.fa-download.iconfont"))
    )

    download_icon.click()
    print(f"DONE: Download button clicked for Index. Downloading to {DATA_PROCESSED_DIR}")

    time.sleep(10)  

finally:
    driver.quit()
