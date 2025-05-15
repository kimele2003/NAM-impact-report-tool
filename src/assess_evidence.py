import os
import csv
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")


def query_gemini(text, source_url, recommendation):
    """Query Gemini with structured prompt."""
    prompt = f"""
    You're helping verify whether a text provides evidence of action on a recommendation or priority from the National Academy of Medicine (NAM). Use the definitions below and respond in the exact format that follows.

    **Definitions:**
    - EVIDENCE:
        - yes = there is clear evidence that the recommended action has been completed or is actively being implemented.
        - partially = there is some indication of progress or intent to act, but the action is not fully completed or confirmed.
        - no = there is no meaningful indication that the action has been taken.
    - NATIONAL_ACADEMY_OF_MEDICINE_MENTIONED:
        - yes = NAM is explicitly referenced as a source of inspiration, proponent or in connection with a recommendation or priority.
        - no = NAM is not being referenced in this context.

    **The recommendation / priority you are evaluating is:**
    {recommendation}

    Please take your time to think through the text step by step. First consider what the text is about and then compare that to the recommendation. Provide a verbal explanation of your reasoning process before you answer.
    Consider whether the text provides evidence that the recommendation or priority is being functionally met, even if it doesn't explicitly state so in the same words or uses different language. Once you have reasoned through the content, respond in the exact format given below, based on your conclusion.
    If there is not any evidence of action that's okay too since this task often requires careful interpretation, and absence of evidence is still a valid and useful finding.

    **Please respond in this exact format:**
    EVIDENCE: [yes | no | partially]
    EXPLANATION: [detailed reasoning explaining why the evidence does or does not support the recommendation]
    CITATION: [short quote from the text supporting the explanation, if EVIDENCE is yes or partially; otherwise write "N/A"]
    NATIONAL_ACADEMY_OF_MEDICINE_MENTIONED: [yes | no]
    NAM_EXPLANATION: [brief explanation of how NAM is mentioned, if yes; otherwise write "N/A"]

    **Text to analyze from {source_url}:**
    {text}
    """

    response = model.generate_content(prompt)
    return response.text


def parse_gemini_response(response_text):
    """Parse structured response from Gemini."""
    evidence = explanation = citation = nam_mentioned = nam_explanation = "N/A"
    for line in response_text.splitlines():
        line = line.strip()
        if line.lower().startswith("evidence:"):
            evidence = line.split(":", 1)[-1].strip().lower()
        elif line.lower().startswith("explanation:"):
            explanation = line.split(":", 1)[-1].strip()
        elif line.lower().startswith("citation:"):
            citation = line.split(":", 1)[-1].strip()
        elif line.lower().startswith("national_academy_of_medicine_mentioned:"):
            nam_mentioned = line.split(":", 1)[-1].strip().lower()
        elif line.lower().startswith("nam_explanation:"):
            nam_explanation = line.split(":", 1)[-1].strip()
    return evidence, explanation, citation, nam_mentioned, nam_explanation


def run():
    """Run the Gemini processing pipeline."""
    base_dir = os.path.dirname(os.path.abspath(__file__)) 
    input_csv = os.path.join(base_dir, '..', 'data', 'webscrape_intermediate_output.csv')
    output_csv = os.path.join(base_dir, '..', 'data', 'webscrape_output.csv')

    with open(input_csv, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    with open(output_csv, "w", newline='', encoding="utf-8") as output_file:
        writer = csv.writer(output_file)
        writer.writerow([
            "Title", "Publication Year", "Domain", "URL", "URL Title", "Extracted Content", "Recommendation",
            "Is Evidence of Action", "Explanation of Relevance", "Citation from Text", "NAM Mentioned", "NAM Explanation",
            "URL Date Last Modified"
        ])

        for row in rows:
            text = row["Extracted Content"]
            url = row["URL"]
            print('Processing URL:', url)
            recommendation = row["Recommendation"]

            if text.startswith("Error"):
                writer.writerow([row["Title"], row["Publication Year"], row["Domain"], url, row["URL Title"], text, recommendation,
                                 "no", "N/A", "N/A", "no", "N/A", row["URL Date Last Modified"]])
            else:
                try:
                    gemini_response = query_gemini(text, url, recommendation)
                    evidence, explanation, citation, nam_mentioned, nam_explanation = parse_gemini_response(gemini_response)
                    writer.writerow([row["Title"], row["Publication Year"], row["Domain"], url, row["URL Title"], text, recommendation,
                                 evidence, explanation, citation, nam_mentioned, nam_explanation, row["URL Date Last Modified"]])
                except Exception as e:
                    print(f"Error running gemini on row {row['Title']}: {e}")
                    writer.writerow([row["Title"], row["Publication Year"], row["Domain"], url, row["URL Title"], text, recommendation,
                                     "no", "N/A", "N/A", "no", "N/A", row["URL Date Last Modified"]])


if __name__ == "__main__":
    run()