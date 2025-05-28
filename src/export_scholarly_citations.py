import os
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from pyairtable import Table

# === Load secrets ===
load_dotenv()
AIRTABLE_PAT = os.getenv("AIRTABLE_PAT")
BASE_ID = os.getenv("AIRTABLE_BASE_ID")

def run():
    # === File path ===
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    DATA_PATH = os.path.join(BASE_DIR, "data", "scholarly_citations_output.csv")

    # === Load the CSV ===
    df = pd.read_csv(DATA_PATH)
    df = df.replace({np.nan: "", np.inf: "", -np.inf: ""})

    # === Connect to Airtable ===
    citation_table = Table(AIRTABLE_PAT, BASE_ID, "Scholarly Citations")

    # === Avoid duplicates ===
    existing_records = citation_table.all()
    existing_keys = {
        (rec['fields'].get('Title', '').strip(), rec['fields'].get('Contexts', '').strip()): rec['id']
        for rec in existing_records
    }

    # === Upload ===
    success_count = 0
    skip_count = 0

    for _, row in df.iterrows():
        publication_title = str(row.get("publication", "")).strip()
        title = str(row.get("title", "")).strip()
        venue = str(row.get("venue", "")).strip()
        url = str(row.get("url", "")).strip()
        contexts = str(row.get("contexts", "")).strip()
        year = str(row.get("year", "")).strip()

        record_key = (title, contexts)

        if record_key in existing_keys:
            print(f"⚠️ Skipping duplicate: {record_key}")
            skip_count += 1
            continue

        record = {
            "Publication Title": publication_title,
            "Title": title,
            "Venue": venue,
            "URL": url,
            "Contexts": contexts,
            "Date Published": year
        }

        try:
            citation_table.create(record)
            success_count += 1
        except Exception as e:
            print(f"⚠️ Failed to create record: {record_key}, error: {e}")

    print(f"✅ Upload complete! {success_count} records created, {skip_count} duplicates skipped.")

if __name__ == "__main__":
    run()