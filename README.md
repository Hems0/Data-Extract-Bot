CBSE SARAS School Data Extraction Bot

This is a Selenium-based Python automation script that extracts data of CBSE-affiliated Senior Secondary Level schools state-wise from the official CBSE SARAS portal and appends it to a Google Spreadsheet.

Website Source
The bot extracts data from the official CBSE SARAS (School Affiliation Re-Engineered Automation System) Schools Directory:

URL: https://saras.cbse.gov.in/saras/AffiliatedList/ListOfSchdirReport

It filters only schools with **Status = "Senior Secondary Level"** (programmatically, after loading the table).

How It Works
1. Hybrid Automation (Manual + Automated):
   - The script opens Chrome and navigates to the SARAS directory page.
   - **Manual steps** (due to unstable UI on government sites):
     - Click "State wise"
     - Select the desired state (e.g., MADHYA PRADESH)
     - Click "SEARCH"
     - Wait for the table to load fully
   - Press **ENTER** in the console when ready.
2. Automated steps:
   - Sets the table to show **100 entries per page**.
   - Automatically paginates through **all pages** (clicks "Next" until disabled).
   - Extracts rows where **Status contains "Senior Secondary Level"**.
   - Assigns serial numbers (continues from existing data in the sheet).
   - Appends the cleaned data to your Google Sheet (no overwriting).

Extracted Columns:
- S No (auto-generated)
- AFF NO & School Code
- State & District
- Status
- School_Name & Head_Name
- Address & Website

Features
- Handles pagination automatically across all pages.
- Resumable: If interrupted, re-run – it appends new data and continues serial numbering.
- Safe for re-runs: No data loss or duplication.
- Works behind corporate proxies (SSL fix included).

Requirements
- Python 3.8+
- Install dependencies:
  ```bash
  pip install selenium webdriver-manager gspread oauth2client
  ```

Setup Instructions

1. Google Sheets API Credentials (Service Account JSON)
To upload data to Google Sheets, you need a **service account key** (JSON file).

Steps:
1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project (or select an existing one).
3. Enable the Google Sheets API and Google Drive API(search in "APIs & Services > Library").
4. Go to APIs & Services > Credentials.
5. Click Create Credentials > Service Account.
6. Fill in a name (e.g., "cbse-sheets-bot") and click Create and Continue.
7. (Optional) Grant roles if needed, then Done.
8. Click on the created service account > Keys tab > Add Key > Create new key.
9. Select JSON and click Create – the file downloads automatically.
10. Rename it to `credentials.json` (or update the filename in the code) and place it in the script folder.

Important:
- Open your Google Spreadsheet.
- Share it with the service account email (found in the JSON file as `"client_email"`, e.g., `your-bot@project.iam.gserviceaccount.com`) and give **Editor** access.

2. Configure the Script
Edit these variables in the code:
```python
STATE_NAME = "MADHYA PRADESH"             # State you will select manually on the site
STATE_SHEET_NAME = "Madhya Pradesh"       # Exact tab name in your Google Sheet (case-sensitive!)
SPREADSHEET_ID = "your-spreadsheet-id-here"  # From the Google Sheet URL
CREDENTIALS_FILE = "credentials.json"   # Your JSON file name
```

- Create separate tabs in your Google Sheet for each state (e.g., "Madhya Pradesh", "Punjab", etc.).
- Header row should be: `S no | AFF NO & School Code | State & District | Status | School_Name & Head_Name | Address & Website`

3. Run the Script
```bash
python bot.py   # or whatever your filename is
```
- Follow the manual steps when prompted.
- Press ENTER when the table loads.
- The bot will extract all pages and append to the sheet.

Notes
- Government sites can be slow – the script includes waits for stability.
- If behind a corporate firewall/proxy, the SSL bypass is already included.
- For a new state: Change `STATE_NAME` and `STATE_SHEET_NAME`, ensure the tab exists, and run.

Disclaimer
This tool is for educational/research purposes. Respect the website's terms and avoid excessive requests.

Enjoy automated CBSE school data collection! 🚀

If you encounter issues, check console output or open an issue on this repo.
