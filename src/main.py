# main.py

import os
from dotenv import load_dotenv

# Step 1: Run full pipeline (fetch + process data)
from src import fetch_input
from src import extract_ctas
from src import generate_links
from src import webscraper 
from src import assess_evidence
from src import scholarly_citations

# Step 2: Export results
from src import export_recommendations
from src import export_scholarly_citations
from src import export_exec_summary

def main():
    print("🔁 Starting full NAM Impact Report pipeline...\n")

    print("📥 Step 1: Fetching raw input from Airtable form...")
    fetch_input.run()

    print("🧠 Step 2: Extracting CTAs from input text...")
    extract_ctas.run()

    print("🔍 Step 3: Generating search queries and link evidence...")
    generate_links.run()

    print("🕸️ Step 4: Running webscraper (placeholder)...")
    webscraper.run()

    print("🕸️ Step 5: Assessing evidence.")
    assess_evidence.run()

    print("📚 Step 6: Gathering scholarly citations (placeholder)...")
    scholarly_citations.run()

    print("📤 Step 7: Exporting recommendations to Airtable...")
    export_recommendations.run()

    print("📤 Step 8: Exporting scholarly citations to Airtable...")
    export_scholarly_citations.run()

    print("📝 Step 9: Generating and uploading executive summary...")
    export_exec_summary.run()

    print("\n✅ Pipeline complete!")

if __name__ == "__main__":
    load_dotenv()
    main()