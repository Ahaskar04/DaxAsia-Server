import gspread
import hashlib
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# 1. Define scopes & authenticate with Google Sheets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS = ServiceAccountCredentials.from_json_keyfile_name("sturdy-dogfish-274710-7bd1c780cdde.json", SCOPE)
client = gspread.authorize(CREDS)

# 2. Open your Google Sheet (single tab approach)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1Dat10wa8A6QQiKgkCcoUL4txD34OhJ3tBLZQb7VmeBI/edit"
sheet = client.open_by_url(SHEET_URL).sheet1  # Use .sheet1 if it's the first tab

# 3. Generate a hashed referral code for a given referrer email
def generate_hashed_referral_code(referrer_email, length=6):
    # Use a secret salt (for security, consider storing this in an environment variable)
    salt = "your_secret_salt"  # Replace with your own secret salt
    hash_obj = hashlib.sha256((referrer_email + salt).encode())
    # Return the first 'length' characters in uppercase
    return hash_obj.hexdigest().upper()[:length]

# 4. Add a new referrer (creates a record with a hashed referral code)
def add_referrer(referrer_email):
    code = generate_hashed_referral_code(referrer_email)
    # Append a row with:
    # [referral_code, referrer_email, signup_email, signup_date, status]
    sheet.append_row([code, referrer_email, "", "", ""])
    return code

# 5. Use referral code: link a new signup to an existing code
def use_referral_code(referral_code, signup_email):
    records = sheet.get_all_records()
    for i, record in enumerate(records, start=2):  # Row 2 is first data row
        if record["Referral Code"] == referral_code:
            # If "Signup Email" is empty, fill it
            if not record["Signup Email"]:
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                sheet.update_cell(i, 3, signup_email)  # Column C -> "Signup Email"
                sheet.update_cell(i, 4, now)           # Column D -> "Signup Date"
                sheet.update_cell(i, 5, "Pending")     # Column E -> "Status"
                return True
            else:
                # If you want multiple signups per code, you can append a new row
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                sheet.append_row([referral_code, record["Referrer Email"], signup_email, now, "Pending"])
                return True
    return False  # Code not found

# 6. Update login status (from "Pending" to "Logged In", etc.)
def update_login_status(signup_email, status="Logged In"):
    records = sheet.get_all_records()
    for i, record in enumerate(records, start=2):
        if record["Signup Email"] == signup_email:
            sheet.update_cell(i, 5, status)  # Column E -> "Status"
            return True
    return False
