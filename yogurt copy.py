from google.oauth2.service_account import Credentials
from openai import OpenAI
from dotenv import load_dotenv
import os

import gspread
import pandas as pd

load_dotenv()
api_key = os.getenv("API_KEY")

ITALIC = "\x1B[3m"
RESET = "\x1B[0m"
PROMPT = "\n\nYour job is to help the user find the requested information from the file \"anton.\" Provide as much information as possible given that the user cannot provide clarification. At the same time, make sure all information provided is accurate. If the user's prompt is incomprehensible, then simply say so."

# Define the scope
scope = ["https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive"]

# Load credentials
creds = Credentials.from_service_account_file(
    "yo-gurt-44-ccecac7bc3ad.json", scopes=scope
)

# Authorize client
client = gspread.authorize(creds)

# Open the sheet
sheet = client.open("anton").sheet1

# Get all data as list of dictionaries
records = sheet.get_all_records()
df = pd.DataFrame(records)

df.to_json("anton.json", orient="records", indent=2)

client = OpenAI(api_key=api_key)

vector_store_id = "vs_682cf8f6cd608191983a970185437105"

with open("anton.json", "rb") as f:
    file = client.vector_stores.files.upload_and_poll(
        vector_store_id=vector_store_id,
        file=f,
    )

if file.status == "completed":
    user_input = input(
        f"What information would you like from the Google Sheet {ITALIC}anton{RESET}?\n").strip()

    while not user_input:
        user_input = input("You didn't enter anything! Try again:\n").strip()

    response = client.responses.create(
        model="gpt-4o",
        input=user_input + PROMPT,
        tools=[{
            "type": "file_search",
            "vector_store_ids": [vector_store_id]
        }]
    )

    print(response.output_text)

    client.responses.delete(
        response_id=response.id
    )
else:
    print("File upload failed:", file.status)

client.files.delete(
    file_id=file.id
)

client.vector_stores.files.delete(
    vector_store_id=vector_store_id,
    file_id=file.id
)
