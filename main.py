from fastapi import FastAPI
from fastapi.responses import JSONResponse
import google.auth
from googleapiclient.discovery import build
from google.oauth2 import service_account
import os
from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI, Query
import json

app = FastAPI()

SERVICE_ACCOUNT_JSON = os.getenv('GOOGLE_CREDS_JSON')

# Ensure the environment variable is set
if not SERVICE_ACCOUNT_JSON:
    raise ValueError("The environment variable GOOGLE_CREDS_JSON not available.")

SERVICE_ACCOUNT_INFO = json.loads(SERVICE_ACCOUNT_JSON)
SPREADSHEET_ID = '1msw7c6rGV5oK9jkG_-5Kff-nB2eDXHEsI4H1vx0BXL0'
RANGE_NAME = 'Sheet1!A1:C20'  # Adjust based on your sheet range

# Authenticate using service account credentials
def authenticate_google_sheets():
    credentials = service_account.Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],)
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


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="FastAPI",
        version="0.1.0",
        routes=app.routes,
    )
    openapi_schema["servers"] = [
        {
            "url": "https://faq-reader.onrender.com"  # Make sure this matches your actual deployed URL
        }
    ]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

# 👇 This is the critical part
app.openapi = custom_openapi

