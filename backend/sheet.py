import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    r"C:\Users\vinay\Downloads\Assessment\data\service_account.json",
    scope
)

client = gspread.authorize(creds)

sheet = client.open(
    "Panache Leads"
).sheet1

def save_lead(data):

    sheet.append_row([
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        data.get("name"),
        data.get("country"),
        data.get("budget"),
        data.get("funding"),
        data.get("timeline"),
        data.get("purpose"),
        data.get("grade")
    ])
    