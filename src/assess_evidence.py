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

    Definitions:

    EVIDENCE:
    yes = there is clear evidence that the recommended action has been fully completed or is actively and concretely being implemented.
    partially = there is direct evidence of concrete progress toward the recommendation (for example, a published plan, an ongoing program, pilot project, or early-stage implementation), but the action is not yet fully realized or confirmed. General discussions, expressions of intent, opinions, or alignment without specific observable action do NOT qualify for "partially."
    no = there is no meaningful or direct indication that the action has been taken.
    NATIONAL_ACADEMY_OF_MEDICINE_MENTIONED:
    yes = NAM is explicitly referenced as a source of inspiration, proponent, or in connection with a recommendation or priority.
    no = NAM is not being referenced in this context.
    The recommendation / priority you are evaluating is:
    {recommendation}

    Please take your time to think through the text step by step. First, consider what the text is about and then compare that to the recommendation. Provide a verbal explanation of your reasoning process before you answer.
    Consider whether the text provides evidence that the recommendation or priority is being functionally met, even if it doesn't explicitly state so in the same words or uses different language.
    Do not select "partially" if the text only includes opinions, priorities, discussions, or intentions without direct, observable steps toward implementation. Only select "partially" if the text demonstrates clear, concrete progress, such as pilot projects, draft plans, or early implementation related to the recommendation.
    If the text appears to have been authored by the National Academy of Medicine, please respond that there is no "evidence of action" and note that in your explanation. This is important for understanding the context and potential bias in the text.
    If there is no evidence of action, that's okay, since this task often requires careful interpretation, and absence of evidence is still a valid and useful finding.

    Please respond in this exact format:
    EVIDENCE: [yes | no | partially]
    EXPLANATION: [detailed reasoning explaining why the evidence does or does not support the recommendation]
    CITATION: [short quote from the text supporting the explanation, if EVIDENCE is yes or partially; otherwise write "N/A"]
    NATIONAL_ACADEMY_OF_MEDICINE_MENTIONED: [yes | no]
    NAM_EXPLANATION: [brief explanation of how NAM is mentioned, if yes; otherwise write "N/A"]

    Text to analyze from {source_url}:
    {text[:100000]}
    """
    response = model.generate_content(prompt)
    return response.text

def query_gemini_multiple(text, source_url, recommendation):
    """Query Gemini with structured prompt."""
    prompt = f"""
    You're helping verify whether a text provides evidence of action on a recommendation or priority from the National Academy of Medicine (NAM). Use the definitions below and respond in the exact format that follows.

    Definitions:

    EVIDENCE:
    yes = there is clear evidence that the recommended action has been fully completed or is actively and concretely being implemented.
    partially = there is direct evidence of concrete progress toward the recommendation (for example, a published plan, an ongoing program, pilot project, or early-stage implementation), but the action is not yet fully realized or confirmed. General discussions, expressions of intent, opinions, or alignment without specific observable action do NOT qualify for "partially."
    no = there is no meaningful or direct indication that the action has been taken.
    NATIONAL_ACADEMY_OF_MEDICINE_MENTIONED:
    yes = NAM is explicitly referenced as a source of inspiration, proponent, or in connection with a recommendation or priority.
    no = NAM is not being referenced in this context.
    The recommendation / priority you are evaluating is:
    {recommendation}

    Please take your time to think through the text step by step. First, consider what the text is about and then compare that to the recommendation. Provide a verbal explanation of your reasoning process before you answer.
    Consider whether the text provides evidence that the recommendation or priority is being functionally met, even if it doesn't explicitly state so in the same words or uses different language.
    Do not select "partially" if the text only includes opinions, priorities, discussions, or intentions without direct, observable steps toward implementation. Only select "partially" if the text demonstrates clear, concrete progress, such as pilot projects, draft plans, or early implementation related to the recommendation.
    If the text appears to have been authored by the National Academy of Medicine, please respond that there is no "evidence of action" and note that in your explanation. This is important for understanding the context and potential bias in the text.
    If there is no evidence of action, that's okay too, since this task often requires careful interpretation, and absence of evidence is still a valid and useful finding.

    Please respond in this exact format:
    EVIDENCE: [yes | no | partially]
    EXPLANATION: [detailed reasoning explaining why the text does or does not support the recommendation]
    CITATION: [short quote from the text supporting the explanation, if EVIDENCE is yes or partially; otherwise write "N/A"]
    NATIONAL_ACADEMY_OF_MEDICINE_MENTIONED: [yes | no]
    NAM_EXPLANATION: [brief explanation of how NAM is mentioned, if yes; otherwise write "N/A"]

    Text to analyze from {source_url}:
    {text[:100000]}
    """

    # Query Gemini three times
    responses = []
    for i in range(3):
        try:
            response = model.generate_content(prompt)
            responses.append(response.text)
        except Exception as e:
            print(f"Error querying Gemini on attempt {i + 1}: {e}")
            responses.append(f"Error: {e}")

    # Use an LLM to evaluate the responses and provide a final judgment
    judge_prompt = f"""
    You are an impartial judge evaluating three responses from an AI model regarding the same task. Your job is to analyze the reasoning and conclusions provided in the responses and determine the most accurate and well-reasoned final judgment.

    **Task**: Determine whether the text provides evidence of action on the recommendation or priority from the National Academy of Medicine (NAM).

    The recommendation / priority you are evaluating is:
    {recommendation}

    **Responses**:
    Response 1:
    {responses[0]}

    Response 2:
    {responses[1]}

    # Response 3:
    # {responses[2]}

    **Instructions**:
    - Carefully evaluate the reasoning and conclusions in each response.
    - Identify any inconsistencies or errors in the reasoning.
    - Cross-check quotes and reasoning against the original text to ensure they are accurate and relevant.
    - Provide a final judgment based on the most accurate and well-reasoned response.
    - If there is no single best response, synthesize a new one based on the strongest reasoning elements from multiple answers.
    - Respond in the following format:

    FINAL_EVIDENCE: [yes | no | partially]
    FINAL_EXPLANATION: [detailed reasoning explaining why this is the most accurate conclusion. don't reference that there are multiple responses, just provide your final explanation, as if it were the only response.]
    FINAL_CITATION: [short quote from the text supporting the explanation, if EVIDENCE is yes or partially; otherwise write "N/A"]
    FINAL_NATIONAL_ACADEMY_OF_MEDICINE_MENTIONED: [yes | no]
    FINAL_NAM_EXPLANATION: [brief explanation of how NAM is mentioned, if yes; otherwise write "N/A. don't reference that there are multiple responses, just provide your final explanation, as if it were the only response."]
    
    Text to analyze from {source_url}:
    {text[:100000]}
    
    """

    try:
        final_response = model.generate_content(judge_prompt)
        return final_response.text
    except Exception as e:
        print(f"Error running judge evaluation: {e}")
        return f"Error: {e}"


def parse_gemini_response(response_text):
    """Parse structured response from Gemini."""
    evidence = explanation = citation = nam_mentioned = nam_explanation = "N/A"
    for line in response_text.splitlines():
        line = line.strip()
        if line.lower().startswith("evidence:") or line.lower().startswith("final_evidence"):
            evidence = line.split(":", 1)[-1].strip().lower()
        elif line.lower().startswith("explanation:") or line.lower().startswith("final_explanation"):
            explanation = line.split(":", 1)[-1].strip()
        elif line.lower().startswith("citation:") or line.lower().startswith("final_citation"):
            citation = line.split(":", 1)[-1].strip()
        elif line.lower().startswith("national_academy_of_medicine_mentioned:") or line.lower().startswith("final_national_academy_of_medicine_mentioned"):
            nam_mentioned = line.split(":", 1)[-1].strip().lower()
        elif line.lower().startswith("nam_explanation:") or line.lower().startswith("final_nam_explanation"):
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
                writer.writerow([row["Title"], row["Publication Year"], row["Domain"], url, row["URL Title"], "Unable to retrieve data", recommendation,
                                 "no", "Unable to retrieve data", "N/A", "no", "N/A", row["URL Date Last Modified"]])
            else:
                try:
                    gemini_response = query_gemini_multiple(text, url, recommendation)
                    evidence, explanation, citation, nam_mentioned, nam_explanation = parse_gemini_response(gemini_response)
                    writer.writerow([row["Title"], row["Publication Year"], row["Domain"], url, row["URL Title"], text, recommendation,
                                 evidence, explanation, citation, nam_mentioned, nam_explanation, row["URL Date Last Modified"]])
                except Exception as e:
                    print(f"Error running gemini on row {row['Title']}: {e}")
                    writer.writerow([row["Title"], row["Publication Year"], row["Domain"], url, row["URL Title"], text, recommendation,
                                     "no", "N/A", "N/A", "no", "N/A", row["URL Date Last Modified"]])


if __name__ == "__main__":
    run()