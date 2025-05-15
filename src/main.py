import os
from src import fetch_input, extract_ctas, generate_links, webscraper, scholarly_citations

def main():
    print("📥 Step 1: Fetching latest submission from Airtable...")
    fetch_input.run()

    print("🧠 Step 2: Extracting Calls to Action (CTAs) using Gemini...")
    extract_ctas.run()

    print("🔍 Step 3: Generating search queries and compiling results...")
    generate_links.run()

    print("🌐 Step 4: Scraping real-world evidence from linked web pages...")
    webscraper.run()

    print("📚 Step 5: Retrieving scholarly citations related to each CTA...")
    scholarly_citations.run()

    print("✅ All steps complete.")

if __name__ == "__main__":
    main()