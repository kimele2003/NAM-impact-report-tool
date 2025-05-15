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

            # Extract metadata
            publication_title = fields.get("Publication Title", "").strip()
            publication_year = fields.get("Publication Year", "").strip()

            # Mark as processed to avoid reprocessing
            table.update(record["id"], {"Processed": True})

            # Save to file in repo root /data
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            data_dir = os.path.join(base_dir, "data")
            os.makedirs(data_dir, exist_ok=True)

            with open(os.path.join(data_dir, "cta_input.txt"), "w", encoding="utf-8") as f:
                f.write(ctas_text)
            
            with open(os.path.join(data_dir, "metadata.txt"), "w", encoding="utf-8") as f:
                f.write(f"{publication_title}\n{publication_year}")

            return

    print("⚠️ No unprocessed CTA submissions found.")

if __name__ == "__main__":
    run()