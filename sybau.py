from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("API_KEY")

openai_client = OpenAI(
    api_key=api_key)

# openai_client.files.delete(file_id="file-U11bDgDvj4zf1Z52j9cFmy")
# openai_client.vector_stores.files.delete(
#     vector_store_id="vs_682cf8f6cd608191983a970185437105", file_id="file-U11bDgDvj4zf1Z52j9cFmy")

print(openai_client.files.list())
print(openai_client.vector_stores.files.list(
    vector_store_id="vs_682cf8f6cd608191983a970185437105"))
