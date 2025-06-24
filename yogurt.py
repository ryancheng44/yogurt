from google.oauth2.service_account import Credentials
from openai import OpenAI
from dotenv import load_dotenv

import gspread
import pandas as pd
import os


# Define the scope
SCOPE = ["https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive"]
VECTOR_STORE_ID = "vs_682cf8f6cd608191983a970185437105"
PROMPT = "Your job is to help the user find the requested information from the file \"anton.\" Provide as much information as possible given that the user cannot provide clarification. At the same time, make sure all information provided is accurate. If the user's prompt is incomprehensible, then simply say so.\n\n"

file_id = ""
cleaned_up = True

# Load credentials
creds = Credentials.from_service_account_file(
    "yo-gurt-44-ccecac7bc3ad.json", scopes=SCOPE
)

# Authorize client
google_client = gspread.authorize(creds)

load_dotenv()
api_key = os.getenv("API_KEY")

openai_client = OpenAI(
    api_key=api_key
)


def setup_vector_store() -> bool:
    # Open the sheet
    sheet = google_client.open("anton").sheet1

    # Get all data as list of dictionaries
    records = sheet.get_all_records()
    df = pd.DataFrame(records)

    df.to_json("anton.json", orient="records", indent=2)

    with open("anton.json", "rb") as f:
        file = openai_client.vector_stores.files.upload_and_poll(
            vector_store_id=VECTOR_STORE_ID,
            file=f,
        )

        global file_id
        file_id = file.id

        global cleaned_up
        cleaned_up = False

    if file.status == "completed":
        return True
    else:
        cleanup()
        return False


def handle_query(user_input: str) -> str:
    response = openai_client.responses.create(
        model="gpt-4o",
        input=PROMPT + user_input,
        tools=[{
            "type": "file_search",
            "vector_store_ids": [VECTOR_STORE_ID]
        }]
    )

    openai_client.responses.delete(
        response_id=response.id
    )

    return response.output_text


def cleanup():
    global cleaned_up
    if cleaned_up:
        return

    openai_client.files.delete(
        file_id=file_id
    )

    openai_client.vector_stores.files.delete(
        vector_store_id=VECTOR_STORE_ID,
        file_id=file_id
    )

    cleaned_up = True

    print(file_id)
    print(openai_client.files.list())
    print(openai_client.vector_stores.files.list(
        vector_store_id=VECTOR_STORE_ID))
