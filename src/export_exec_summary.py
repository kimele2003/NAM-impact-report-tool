import os
import pandas as pd
from dotenv import load_dotenv
from pyairtable import Table
import google.generativeai as genai

# === Load environment variables ===
load_dotenv()
AIRTABLE_PAT = os.getenv("AIRTABLE_PAT")
BASE_ID = os.getenv("AIRTABLE_BASE_ID")
GENAI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel("models/gemini-2.0-flash") 

def run():
    # === File paths ===
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    recommendations_path = os.path.join(data_dir, "webscrape_output.csv")
    citations_path = os.path.join(data_dir, "scholarly_citations_output.csv")
    cta_input_path = os.path.join(data_dir, "cta_input.txt")
    METADATA_PATH = os.path.join(data_dir, "metadata.txt")

    # === Executive Summary Generator ===
    def generate_executive_summary(reco_path, citations_path, excerpt_path):
        reco_df = pd.read_csv(reco_path)
        cite_df = pd.read_csv(citations_path)

        with open(excerpt_path, "r", encoding="utf-8") as f:
            excerpt = f.read()[:2000]  # Trim to 2000 characters

        # === Load publication title and year ===
        with open(METADATA_PATH, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
            publication_year = lines[-1]
            publication_title = " ".join(lines[:-1])

        prompt = f"""
            Below is a short excerpt from the publication to provide context only. **Do not quote or cite it directly**:
            --- BEGIN EXCERPT ---
            {excerpt}
            --- END EXCERPT ---

            Write a 3-part executive summary (250 words max) for members of the National Academy of Medicine. The summary should be written in clear, non-technical language and must be self-contained. Do not include any introductory phrases about writing the summary or references to the excerpt above. Simply present the summary directly.

            Structure your response as follows:

            1. Overview of the Report
            - Title: *{publication_title}*
            - A 1–2 sentence summary of the report’s purpose, key themes, or findings

            2. Evidence of Recommendations
            - A brief description of observed progress (e.g., policy changes, advisory boards, funding efforts)
            - Highlight any recommendations or priorities with notable evidence of follow-through
            - Mention 1–2 relevant external sources (e.g., .gov, WHO, NIH, NYTimes) showing this impact

            3. Publication Citations & Scholarly Uptake
            - Mention journals, agencies, or organizations that cited it
            - Describe trends: common citation topics, academic vs. policy use, or disciplinary/geographic patterns
            """

        response = model.generate_content(prompt)
        raw_output = response.text.strip()

        # Remove all markdown bold/italic markers: ** and *
        clean_output = re.sub(r"(\*\*|\*)", "", raw_output)

        # Clean up any double newlines
        formatted_output = re.sub(r"\n{2,}", "\n\n", clean_output.strip())

        return publication_title, formatted_output

    # === Upload to Airtable ===
    def upload_summary_to_airtable(title, summary):
        table = Table(AIRTABLE_PAT, BASE_ID, "Executive Summaries")

        # Check if entry already exists
        existing = table.all()
        titles = {rec['fields'].get("Publication Title", "").strip(): rec['id'] for rec in existing}

        if title in titles:
            print(f"📝 Updating existing summary for: {title}")
            table.update(titles[title], {"Publication Title": title, "Executive Summary": summary})
        else:
            print(f"✅ Creating new summary for: {title}")
            table.create({"Publication Title": title, "Executive Summary": summary})

    try:
        pub_title, summary_text = generate_executive_summary(recommendations_path, citations_path, cta_input_path)
        upload_summary_to_airtable(pub_title, summary_text)
        print("✅ Executive summary uploaded successfully.")
    except Exception as e:
        print(f"❗ Error generating or uploading summary: {e}")

if __name__ == "__main__":
    run()