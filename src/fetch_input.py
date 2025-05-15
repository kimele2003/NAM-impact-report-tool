import os
from pyairtable import Table, Api
from dotenv import load_dotenv

# Load secrets from .env
load_dotenv()

# Airtable setup
AIRTABLE_PAT = os.getenv("AIRTABLE_PAT")
BASE_ID = "appO6HDSdKA5DkzUr"
TABLE_NAME = "Uploaded Publications"
FIELD_NAME = "CTAs"

def run():
    api = Api(AIRTABLE_PAT)
    table = api.table(BASE_ID, TABLE_NAME)

    # Get records, most recent first
    records = table.all(sort=["-Upload Timestamp"])

    for record in records:
        fields = record.get("fields", {})
        ctas_text = fields.get(FIELD_NAME, "").strip()
        already_processed = fields.get("Processed", False)

        if ctas_text and not already_processed:
            print(f"✅ Found CTAs:\n{ctas_text[:250]}...\n")

            # Mark as processed to avoid reprocessing
            table.update(record["id"], {"Processed": True})

            # Save to file
            os.makedirs("data", exist_ok=True)
            with open("data/CTA_input.txt", "w", encoding="utf-8") as f:
                f.write(ctas_text)

            return

    print("⚠️ No unprocessed CTA submissions found.")

if __name__ == "__main__":
    run()