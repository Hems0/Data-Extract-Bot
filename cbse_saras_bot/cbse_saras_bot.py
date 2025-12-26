from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ================= CONFIG =================
STATE_NAME = "WEST BENGAL"
REQUIRED_STATUS = "Senior Secondary Level"
STATE_SHEET_NAME = "West Bengal"
SPREADSHEET_ID = "1PCltNpGNfA6rnG7GhhdcAgx0fRWScNZKazXsKQVLnfw"
# =========================================

# ================= BROWSER =================
options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

driver.get("https://saras.cbse.gov.in/saras/AffiliatedList/ListOfSchdirReport")

print("\n🟡 MANUAL STEPS REQUIRED:")
print("1️⃣ Click 'State wise'")
print(f"2️⃣ Select State = {STATE_NAME}")
print("3️⃣ Click SEARCH")
print("4️⃣ Wait until table is fully visible")

input("👉 AFTER you see the table data, press ENTER here to start extraction...")

# =================================================
# SET SHOW ENTRIES TO 100 USING SELENIUM
# =================================================
try:
    length_select = driver.find_element(By.CSS_SELECTOR, ".dataTables_length select")
    select = Select(length_select)
    select.select_by_value("100")
    time.sleep(3)  # Increased wait for table reload
    print("✅ Set table to show 100 entries")
except:
    print("⚠️ Could not change entries count")

# =================================================
# SCRAPE + FILTER BY STATUS
# =================================================
data = []

# Get current data from sheet to continue serial_no
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "credentials.json", scope
)
client = gspread.authorize(creds)

sheet = client.open_by_key(
    SPREADSHEET_ID
).worksheet(STATE_SHEET_NAME)

all_values = sheet.get_all_values()
serial_no = len(all_values) if all_values else 1  # If empty, start from 1 (but header should be there)

# Assume header is always present; if len==0 or 1, start from 1
if len(all_values) <= 1:
    serial_no = 1
else:
    serial_no = len(all_values)  # Next serial is current rows (header + data) 

while True:
    rows = driver.find_elements(By.CSS_SELECTOR, "table.dataTable tbody tr")

    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        if len(cols) < 6:
            continue

        status_text = cols[3].text

        if REQUIRED_STATUS not in status_text:
            continue

        data.append([
            serial_no,
            cols[1].text,
            cols[2].text,
            cols[3].text.strip(),
            cols[4].text,
            cols[5].text
        ])
        serial_no += 1

    try:
        next_li = driver.find_element(By.CSS_SELECTOR, ".dataTables_paginate .paginate_button.next")
        if "disabled" in next_li.get_attribute("class"):
            break
        next_btn = next_li.find_element(By.TAG_NAME, "a")
        next_btn.click()
        time.sleep(2)  # Slightly increased for stability
    except:
        break

driver.quit()

print(f"✅ Total Senior Secondary schools found: {len(data)}")

# =================================================
# GOOGLE SHEETS - APPEND MODE
# =================================================
if data:
    # No clear, just append
    sheet.append_rows(data)

print(f"✅ Data appended to '{STATE_SHEET_NAME}' sheet")