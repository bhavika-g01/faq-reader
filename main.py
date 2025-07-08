from fastapi import FastAPI
from fastapi.responses import JSONResponse
import google.auth
from googleapiclient.discovery import build
from google.oauth2 import service_account
import os

app = FastAPI()

SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

# Ensure the environment variable is set
if not SERVICE_ACCOUNT_FILE:
    raise ValueError("The environment variable GOOGLE_APPLICATION_CREDENTIALS is not set.")

SPREADSHEET_ID = '1msw7c6rGV5oK9jkG_-5Kff-nB2eDXHEsI4H1vx0BXL0'
RANGE_NAME = 'Sheet1!A1:C20'  # Adjust based on your sheet range

# Authenticate using service account credentials
def authenticate_google_sheets():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
    )
    service = build('sheets', 'v4', credentials=credentials)
    return service

# Function to fetch data from Google Sheets
def get_faq_data():
    service = authenticate_google_sheets()

    # Read the sheet
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    rows = result.get('values', [])
    return rows

@app.get("/faq")
async def fetch_faq():
    data = get_faq_data()
    if not data:
        return JSONResponse(status_code=404, content={"message": "No FAQ data found"})
    
    faq_list = []
    for row in data:
        if len(row) >= 2:
            faq_list.append({"question": row[0], "answer": row[1]})

    return JSONResponse(content={"faqs": faq_list})

