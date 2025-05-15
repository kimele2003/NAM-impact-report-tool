import os
import re
import pandas as pd
from dotenv import load_dotenv
import google.generativeai as genai

def run():
    # === Load environment variables ===
    load_dotenv()

    # === Load CTA input text ===
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    INPUT_PATH = os.path.join(base_dir, "data", "cta_input.txt")
    OUTPUT_CSV = os.path.join(base_dir, "data", "cta_queries.csv")

    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        cta_text = f.read()

    # === Gemini setup ===
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(model_name="models/gemini-2.0-flash")

    # === Extract individual CTAs ===
    def extract_calls_to_action(text):
        prompt = (
            "From the following policy report text, extract **all** labeled calls to action, including all items labeled as 'Recommendation', 'Priority', or similar, even if they are sub-items (e.g., 'Priority 1-2', 'Priority 1-3'). "
            "Preserve their original wording and order. Do not summarize or skip any items. "
            "Make sure to include indented sub-points or bullet points under each recommendation or priority."

            f"{text[:20000]}"  # Truncate to 15000 characters max for Gemini input limit
        )
        response = model.generate_content(prompt)
        return response.text.strip()

    # === Count number of extracted CTAs ===
    def count_ctas_in_output(cta_output):
        # Match both "Recommendation A.1:" and "Priority 1-1:"
        pattern = r"\b(?:Recommendation|Priority)\s+[A-Z]?\d+[-.]?\d*:"
        matches = re.findall(pattern, cta_output)
        print('CTA titles:', matches)
        return len(matches)

    cta_output = extract_calls_to_action(cta_text)
    cta_count = count_ctas_in_output(cta_output)
    print(f"{cta_count} CTAs identified in cta_output")

    # Save Gemini-generated CTAs to file
    CTA_OUTPUT_PATH = os.path.join(base_dir, "data", "cta_output.txt")
    with open(CTA_OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(cta_output)
    print(f"✅ CTA output saved to {CTA_OUTPUT_PATH}")

if __name__ == "__main__":
    run()