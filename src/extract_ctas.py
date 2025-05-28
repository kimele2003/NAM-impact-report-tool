import os
import re
import pandas as pd
from dotenv import load_dotenv
import google.generativeai as genai

# === Load environment variables ===
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# === Gemini setup ===
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(model_name="models/gemini-2.0-flash")

# === Extract individual CTAs ===
def extract_calls_to_action(text):
    prompt = (
        "From the following policy report text, extract **all** labeled calls to action, including all items labeled as 'Recommendation', 'Priority', or similar, even if they are sub-items (e.g., 'Priority 1-2', 'Priority 1-3'). "
        "Also extract calls to action that follow introductory phrases like “We have identified five priorities,” “The following are key actions,” or other similar lead-ins, even if individual items are numbered (e.g. 1-5) but not explicitly labeled as priorities or recommendations."
        "Do NOT change the titles, numbering, or wording of the recommendations. "
        "Make sure to include indented sub-points or bullet points under each recommendation or priority."

        f"{text[:30000]}"  # Truncate to 15000 characters max for Gemini input limit
    )
    response = model.generate_content(prompt)
    try:
        return response.text.strip()
    except ValueError:
        print("⚠️ Gemini blocked the output due to copyright concerns.")
        return "NO_RESPONSE"

# === Count number of extracted CTAs ===
def count_ctas_in_output(cta_output):
    # Match headings like "Recommendation A.1:" or "Priority 1-2:"
    pattern = r"^(Recommendation|Priority)\s+[A-Z]?\d+(?:[-.]\d+)?\s*:", re.IGNORECASE | re.MULTILINE
    matches = re.findall(pattern[0], cta_output, flags=pattern[1])
    
    print("CTA titles found:")
    for m in matches:
        print("-", m)
    return len(matches)

def run():
    # === Load CTA input text ===
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    INPUT_PATH = os.path.join(base_dir, "data", "cta_input.txt")
    OUTPUT_CSV = os.path.join(base_dir, "data", "cta_queries.csv")

    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        cta_text = f.read()

    cta_output = extract_calls_to_action(cta_text)
    print("🔍 Preview of Gemini raw output:\n", cta_output[:1000]) 
    cta_count = count_ctas_in_output(cta_output)
    print(f"{cta_count} CTAs identified in cta_output")

    # Save Gemini-generated CTAs to file
    CTA_OUTPUT_PATH = os.path.join(base_dir, "data", "cta_output.txt")
    with open(CTA_OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(cta_output)
    print(f"✅ CTA output saved to {CTA_OUTPUT_PATH}")

if __name__ == "__main__":
    run()