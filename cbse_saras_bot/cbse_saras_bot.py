import os
os.environ['WDM_SSL_VERIFY'] = '0'  # Fixes SSL certificate error for webdriver_manager in corporate networks

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
STATE_NAME = "PUNJAB"                    # Change this to the state you will select manually
REQUIRED_STATUS = "Senior Secondary Level"
STATE_SHEET_NAME = "Punjab"               # Must match the exact tab name in your Google Sheet
SPREADSHEET_ID = "1PCltNpGNfA6rnG7GhhdcAgx0fRWScNZKazXsKQVLnfw"
CREDENTIALS_FILE = "new_credentials.json"  # Your new service account key file
# =========================================

# ================= BROWSER SETUP =================
options = Options()
options.add_argument("--start-maximized")
# options.add_argument("--headless")  # Uncomment if you want to run without opening browser (not recommended for this hybrid flow)

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

driver.get("https://saras.cbse.gov.in/saras/AffiliatedList/ListOfSchdirReport")

print("\n🟡 MANUAL STEPS REQUIRED:")
print("1️⃣ Click on 'State wise'")
print(f"2️⃣ Select State: {STATE_NAME}")
print("3️⃣ Click SEARCH")
print("4️⃣ Wait until the school table loads fully with data")

input("👉 When the table is visible and loaded, press ENTER here to begin automated extraction...")

# =================================================
# SET "SHOW ENTRIES" TO 100
# =================================================
try:
    length_select_element = driver.find_element(By.CSS_SELECTOR, ".dataTables_length select")
    select = Select(length_select_element)
    select.select_by_value("100")
    time.sleep(4)  # Give time for table to reload with 100 entries
    print("✅ Successfully set to show 100 entries per page")
except Exception as e:
    print("⚠️ Could not set entries to 100:", e)

# =================================================
# CONNECT TO GOOGLE SHEETS
# =================================================
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
client = gspread.authorize(creds)

sheet = client.open_by_key(SPREADSHEET_ID).worksheet(STATE_SHEET_NAME)

# Get current number of rows to continue serial number
all_values = sheet.get_all_values()
if len(all_values) <= 1:  # Only header or empty sheet
    serial_no = 1
else:
    serial_no = len(all_values)  # Next row after existing data (header + previous rows)

print(f"📊 Starting serial number from: {serial_no}")

# =================================================
# SCRAPE ALL PAGES
# =================================================
data = []

while True:
    # Wait a moment for rows to be present
    time.sleep(1)
    rows = driver.find_elements(By.CSS_SELECTOR, "table.dataTable tbody tr")

    if len(rows) == 0:
        print("⚠️ No rows found on this page. Possibly still loading...")
        time.sleep(3)
        continue

    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        if len(cols) < 6:
            continue  # Skip incomplete or "No data" rows

        status_text = cols[3].text.strip()

        if REQUIRED_STATUS not in status_text:
            continue  # Only Senior Secondary Level schools

        data.append([
            serial_no,
            cols[1].text.strip(),
            cols[2].text.strip(),
            cols[3].text.strip(),
            cols[4].text.strip(),
            cols[5].text.strip()
        ])
        serial_no += 1

    # Check for next page
    try:
        next_button_li = driver.find_element(By.CSS_SELECTOR, ".dataTables_paginate .paginate_button.next")
        if "disabled" in next_button_li.get_attribute("class"):
            print("✅ Reached the last page.")
            break

        next_button = next_button_li.find_element(By.TAG_NAME, "a")
        driver.execute_script("arguments[0].click();", next_button)  # More reliable click
        time.sleep(3)  # Wait for next page to load
        print(f"⬇️ Moving to next page... (Collected {len(data)} schools so far)")

    except Exception as e:
        print("⚠️ No more pages or error in pagination:", e)
        break

driver.quit()

print(f"\n✅ Extraction complete! Found {len(data)} Senior Secondary schools this run.")

# =================================================
# APPEND TO GOOGLE SHEET
# =================================================
if data:
    sheet.append_rows(data)
    print(f"✅ Successfully appended {len(data)} rows to the '{STATE_SHEET_NAME}' sheet.")
else:
    print("⚠️ No new data found to append.")

print("\n🎉 Script finished. You can now run it again for another state or resume later — it will continue from where it left off!")
