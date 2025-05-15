import pandas as pd
import numpy as np
from pyairtable import Table, Api
import os
from dotenv import load_dotenv

def run():
    # Load API key from .env
    load_dotenv()
    AIRTABLE_PAT = os.getenv("AIRTABLE_PAT")
    BASE_ID = os.getenv("AIRTABLE_BASE_ID")

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    data_path = os.path.join(base_dir, "data", "webscrape_output.csv")
    recommendation_df = pd.read_csv(data_path)
    recommendation_df = recommendation_df.replace({np.nan: "", np.inf: "", -np.inf: ""})

    api = Api(AIRTABLE_PAT)
    recommendation_table = api.table(BASE_ID, "Recommendations")

    # Fetch existing records to avoid duplicates
    existing_records = recommendation_table.all()
    existing_keys = {
        (rec['fields'].get('Publication Title', '').strip(), rec['fields'].get('Recommendation', '').strip()): rec['id']
        for rec in existing_records
    }

    nam_option_mapping = {"yes": "Yes", "no": "No"}
    evidence_option_mapping = {"yes": "Yes", "no": "No", "partially": "Partially"}

    success_count = 0
    fail_count = 0
    skipped_count = 0
    skipped_invalid_evidence = 0
    skipped_invalid_nam = 0

    for idx, row in recommendation_df.iterrows():
        try:
            pub_title = str(row.get("Publication Title", "")).strip()
            recommendation = str(row.get("Recommendation", "")).replace("*", "").replace('"', '').replace("'", "").strip()
            domain = str(row.get("Domain", "")).strip()

            is_evidence_raw = str(row.get("Is Evidence of Action", "")).strip().lower()
            nam_mentioned_raw = str(row.get("NAM Mentioned", "")).strip().lower()

            is_evidence = evidence_option_mapping.get(is_evidence_raw)
            nam_mentioned = nam_option_mapping.get(nam_mentioned_raw)

            if is_evidence is None:
                print(f"⚠️ Skipping row {idx} due to invalid Is Evidence of Action value: '{is_evidence_raw}'")
                skipped_count += 1
                skipped_invalid_evidence += 1
                continue

            if nam_mentioned is None:
                print(f"⚠️ Skipping row {idx} due to invalid NAM Mentioned value: '{nam_mentioned_raw}'")
                skipped_count += 1
                skipped_invalid_nam += 1
                continue

            record_data = {
                "Publication Title": pub_title,
                "Publication Year": str(row.get("Publication Year", "")).strip(),
                "Recommendation": recommendation,
                "Domain": domain,
                "URL": str(row.get("URL", "")).strip(),
                "URL Title": str(row.get("URL Title", "")).strip(),
                "Extracted Content": str(row.get("Extracted Content", "")).strip(),
                "Citation from Text": str(row.get("Citation from Text", "")).strip(),
                "Is Evidence of Action": is_evidence,
                "Explanation of Relevance": str(row.get("Explanation of Relevance", "")).strip(),
                "NAM Mentioned": nam_mentioned,
                "NAM Explanation": str(row.get("NAM Explanation", "")).strip()
            }

            record_key = (pub_title, recommendation)
            if record_key in existing_keys:
                recommendation_table.update(existing_keys[record_key], record_data)
            else:
                recommendation_table.create(record_data)
            
            date_val = row.get("URL Date Last Modified", "")
            if pd.isna(date_val) or str(date_val).strip().lower() in {"nat", "nan"}:
                record_data["URL Date Last Modified"] = ""
            else:
                record_data["URL Date Last Modified"] = str(date_val).strip()

            success_count += 1

        except Exception as e:
            fail_count += 1
            print(f"⚠️ Error on row {idx}: {e}")

    print(f"✅ Upload complete!")
    print(f"✅ {success_count} records processed successfully")
    print(f"⚠️ {fail_count} records failed due to exceptions")
    print(f"⚠️ {skipped_count} rows skipped due to invalid data")
    print(f"   └─ {skipped_invalid_evidence} skipped for invalid Is Evidence of Action")
    print(f"   └─ {skipped_invalid_nam} skipped for invalid NAM Mentioned")

if __name__ == "__main__":
    run()