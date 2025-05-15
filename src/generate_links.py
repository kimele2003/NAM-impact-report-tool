import os
import re
import time
import requests
import pandas as pd
from dotenv import load_dotenv
import google.generativeai as genai
from datetime import datetime

# === Load environment variables ===
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

# === Configure Gemini ===
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("models/gemini-2.0-flash")

# === Paths ===
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
data_dir = os.path.join(base_dir, "data")
INPUT_PATH = os.path.join(data_dir, "cta_output.txt")
METADATA_PATH = os.path.join(data_dir, "metadata.txt")

# === Load CTA output text ===
with open(INPUT_PATH, "r", encoding="utf-8") as f:
    cta_output = f.read()

# === Load publication title and year ===
with open(METADATA_PATH, "r", encoding="utf-8") as f:
    publication_title = f.readline().strip()
    publication_year = f.readline().strip()

# === Create output path ===
# timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # e.g., 20240514_145700
# safe_title = re.sub(r'\W+', '_', publication_title.strip())[:40] or "Untitled"
# filename = f"{safe_title}_{timestamp}_CTA_Links.csv"
# OUTPUT_CSV = os.path.join(data_dir, filename)

filename = "cta_search_results.csv"
OUTPUT_CSV = os.path.join(data_dir, filename)

# === STEP 1: Extract CTA blocks ===
def extract_cta_blocks(cta_output):
    matches = re.findall(
        r"(?s)(?:\*+\s+)?(Priority\s+\d+(?:-\d+)?:(?:.*?))(?=\n\s*\*+\s+Priority\s+\d|$)",
        cta_output,
        re.IGNORECASE
    )
    return [m.strip() for m in matches]

# === STEP 2: Generate search queries using Gemini ===
def generate_search_queries_for_ctas(cta_list):
    all_queries = []
    for cta in cta_list:
        prompt = f"""
            You are a health policy analyst. For the following Call to Action (CTA), identify key stakeholders and generate 3 flexible Google search queries that could be used to find real-world mentions or updates.

            Each query should use one of these trusted domains:
            site:usa.gov, site:nih.gov, site:hhs.gov, site:who.int, site:pubmed.ncbi.nlm.nih.gov, site:nytimes.com

            Avoid overly rigid or overly quoted phrasing. Use combinations of key terms that are likely to co-occur in real-world reporting.

            Format:
            CTA: ...
            Stakeholders: ...
            Search Queries:
            - ...
            - ...
            - ...

            CTA:
            "{cta}"
            """
        response = model.generate_content(prompt)
        all_queries.append(response.text.strip())
        print("🔍 Gemini output for CTA:\n", response.text.strip(), "\n---")
    return all_queries

# === STEP 3: Google search for each query ===
def search_google(query, api_key, cse_id):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": cse_id,
        "q": query,
        "num": 5
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"❗ Google CSE API Error: {response.status_code} {response.text}")
        return []

    if not response.json().get("items"):
        print(f"⚠️ No search results returned for: {query}")

    time.sleep(1)

    results = []
    for item in response.json().get("items", []):
        title = item.get("title", "")
        url = item.get("link", "")
        snippet = item.get("snippet", "")
        metatags = item.get("pagemap", {}).get("metatags", [{}])[0]
        date = (
            metatags.get("article:published_time") or
            metatags.get("article:modified_time") or
            metatags.get("og:updated_time") or
            metatags.get("datePublished") or
            metatags.get("date") or
            ""
        )
        if date:
            date = re.sub(r"T.*", "", date).strip()

        results.append((title, url, snippet, date))
    return results

# === STEP 4: Compile into DataFrame ===
def compile_results(cta_queries, api_key, cse_id, publication_title="", publication_year=""):
    def clean_generic(text):
        return re.sub(r'[*"“”]+', '', text).strip()

    rows = []
    for block in cta_queries:
        cta_match = re.search(r"CTA:\s*(.*?)\nStakeholders:", block, re.DOTALL)
        cta = clean_generic(cta_match.group(1)) if cta_match else ""

        stakeholders_match = re.search(r"Stakeholders:\s*(.*?)\nSearch Queries:", block, re.DOTALL)
        stakeholders = clean_generic(stakeholders_match.group(1)) if stakeholders_match else ""

        queries_block = re.search(r"Search Queries:\s*(.+)", block, re.DOTALL)
        query_matches = re.findall(r"(?:[-*]|\d+\.)\s+(.+)", queries_block.group(1)) if queries_block else []
        query_matches = query_matches[:2]  # limit to 2 per CTA

        print(f"✅ Queries extracted:\n{query_matches}\n---")
        if not query_matches:
            print(f"⚠️ No queries found for block:\n{block}\n---")
        
        for query in query_matches:
            print(f"🌐 Searching for query: {query}")
            search_results = search_google(query, api_key, cse_id)
            for title, url, snippet, date in search_results:
                rows.append({
                    "Publication Title": publication_title,
                    "Publication Year": publication_year,
                    "CTA": cta,
                    "Stakeholders": stakeholders,
                    "Query": clean_generic(query),
                    "Title": clean_generic(title),
                    "URL": url,
                    "Snippet": clean_generic(snippet),
                    "Source Date": date
                })
    return pd.DataFrame(rows)

if __name__ == "__main__":
    # === Run full pipeline ===
    cta_list = extract_cta_blocks(cta_output)
    query_outputs = generate_search_queries_for_ctas(cta_list)
    df = compile_results(query_outputs, GOOGLE_API_KEY, GOOGLE_CSE_ID, publication_title, publication_year)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"{len(df)} rows written to {OUTPUT_CSV}")