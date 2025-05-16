import google.generativeai as genai
import pandas as pd
import os
from dotenv import load_dotenv

# === Load environment variables ===
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# === Configure Gemini ===
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("models/gemini-2.0-flash")

cta_input = """
    Recommendation C.8: By the end of 2016, the World
    Health Assembly should agree on new mechanisms for
    holding governments publicly accountable for perfor-
    mance under the International Health Regulations
    and broader global health risk framework, as detailed
    in Recommendation B.2, including:
    • protocols for avoiding suppression or delays in
    data and alerts, and
    • protocols for avoiding unnecessary restrictions on
    trade or travel.
    We support the World Bank’s proposal to create a
    Pandemic Emergency Financing Facility as a comple-
    ment to WHO’s contingency fund. If innovative in-
    surance and capital market mechanisms can be dem-
    onstrated to be both economically viable and practical,
    these could potentially represent an attractive new
    source of funds. While clearly politically challenging
    to implement, binding contingent commitments from
    donor governments represent an economic and $exible
    alternative.
    Recommendation C.9: By the end of 2016, the World
    Bank should establish the Pandemic Emergency Fi-
    nancing Facility as a rapidly deployable source of funds
    to support pandemic response.
    To ease fiscal pressure on governments that raise
    infectious disease outbreak alerts, and reduce the in-
    centive to avoid doing so, the IMF should make clear
    that it is in a position to provide budgetary assistance
    when needed.
    Recommendation C.10: By the end of 2016, the Inter-
    national Monetary Fund should ensure that it has the
    demonstrable capability to provide budgetary support
    to governments raising alerts of outbreaks, perhaps
    through its existing Rapid Credit Facility.
"""

# Define example prompts
example_prompts = [
    {
        "task": "CTA Extraction",
        "input": "From the following policy report text, extract **all** labeled calls to action, including all items labeled as 'Recommendation', 'Priority', or similar, even if they are sub-items (e.g., 'Priority 1-2', 'Priority 1-3'). "
        "Do NOT change the titles, numbering, or wording of the recommendations. "
        "Make sure to include indented sub-points or bullet points under each recommendation or priority."
        f"{cta_input}"
    }
]

# Generate and collect outputs
examples = []
for example in example_prompts:
    response = model.generate_content(example["input"])
    examples.append({
        "Task": example["task"],
        "Input": example["input"],
        "Output": response.text.strip()
    })

print(examples)