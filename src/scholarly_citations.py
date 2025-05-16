import requests
import time
import csv
import os
import tldextract
import re
from dotenv import load_dotenv

load_dotenv()

# Constants
SEMANTIC_SCHOLAR_BASE_URL = "https://api.semanticscholar.org/graph/v1"
GOOGLE_SCHOLAR_API_URL = "https://serpapi.com/search"
USER_AGENT = "Mozilla/5.0 Academic Paper Tool"
DEFAULT_LIMIT = 200

# Utility Functions
def extract_base_domain(url):
    """Extract the base domain from a URL."""
    extracted = tldextract.extract(url)
    return f"{extracted.domain}.{extracted.suffix}"


def extract_year(summary):
    """Extract a 4-digit year from a string."""
    match = re.search(r'\b(19|20)\d{2}\b', summary)
    return match.group(0) if match else "Unknown"


# Semantic Scholar Functions
def search_paper_by_title(title, api_key=None):
    """
    Search for a paper by title in Semantic Scholar and return its ID.
    """
    url = f"{SEMANTIC_SCHOLAR_BASE_URL}/paper/search"
    headers = {"User-Agent": USER_AGENT}
    if api_key:
        headers["x-api-key"] = api_key

    params = {
        "query": title,
        "fields": "paperId,title,year,authors",
        "limit": 5,
    }

    try:
        print(f"Searching for paper: {title}...")
        time.sleep(0.5)  # Respect rate limits
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        if not data.get("data"):
            print("No papers found matching this title.")
            return None

        # Automatically select the first result
        paper_id = data["data"][0]["paperId"]
        print(f"Found paper: {data['data'][0]['title']} (ID: {paper_id})")
        return paper_id

    except requests.exceptions.RequestException as e:
        print(f"Error searching for paper: {e}")
        return None


def get_citations_with_context(paper_id, limit=DEFAULT_LIMIT, api_key=None):
    """
    Get papers that cite the specified paper along with citation contexts.
    """
    url = f"{SEMANTIC_SCHOLAR_BASE_URL}/paper/{paper_id}/citations"
    headers = {"User-Agent": USER_AGENT}
    if api_key:
        headers["x-api-key"] = api_key

    citations = []
    offset = 0

    while len(citations) < limit:
        params = {
            "fields": "citingPaper.title,citingPaper.url,citingPaper.venue,citingPaper.year,contexts",
            "limit": 100,
            "offset": offset,
        }

        try:
            print(f"Fetching citations (offset: {offset})...")
            time.sleep(1)  # Respect rate limits
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            for citation in data.get("data", []):
                contexts = citation.get("contexts", [])
                citations.append({
                    "title": citation["citingPaper"]["title"],
                    "venue": citation["citingPaper"]["venue"],
                    "url": citation["citingPaper"]["url"],
                    "contexts": " || ".join(contexts) if contexts else "",
                    "year": citation["citingPaper"]["year"],
                })

            if len(data.get("data", [])) < 100:
                break  # No more results
            offset += 100

        except requests.exceptions.RequestException as e:
            print(f"Error fetching citations: {e}")
            break

    return citations[:limit]


# Google Scholar Functions
def search_paper_google_scholar(title):
    """
    Search for a paper by title in Google Scholar and return its citation ID.
    """
    params = {
        "engine": "google_scholar",
        "q": title,
        "api_key": os.getenv("SERP_API_KEY"),
    }

    try:
        response = requests.get(GOOGLE_SCHOLAR_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        first_result = data.get("organic_results", [])[0]
        return first_result.get("inline_links", {}).get("cited_by", {}).get("cites_id")
    except (IndexError, requests.exceptions.RequestException) as e:
        print(f"Error searching Google Scholar: {e}")
        return None


def get_citing_papers_google_scholar(cites_id, max_pages=3):
    """
    Get citing papers from Google Scholar using a citation ID.
    """
    citing_papers = []

    for page in range(max_pages):
        params = {
            "engine": "google_scholar",
            "api_key": os.getenv("SERP_API_KEY"),
            "cites": cites_id,
            "start": page * 10,
        }

        try:
            response = requests.get(GOOGLE_SCHOLAR_API_URL, params=params)
            response.raise_for_status()
            data = response.json()

            for result in data.get("organic_results", []):
                citing_papers.append({
                    "title": result.get("title", "N/A"),
                    "venue": extract_base_domain(result.get("link", "")),
                    "url": result.get("link", ""),
                    "contexts": "",
                    "year": extract_year(result.get("publication_info", {}).get("summary", "")),
                })

        except requests.exceptions.RequestException as e:
            print(f"Error fetching citing papers: {e}")
            break

    return citing_papers


# File Handling
def save_to_csv(data, filename):
    """
    Save citation data to a CSV file.
    """
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["title", "venue", "url", "contexts", "year"])
        writer.writeheader()
        writer.writerows(data)
    print(f"Saved data to {filename}")


# Main Function
def get_citations_by_title(title, filename):
    """
    Get citations for a paper by title using Semantic Scholar or Google Scholar.
    """
    # Try Semantic Scholar first
    paper_id = search_paper_by_title(title)
    if paper_id:
        citations = get_citations_with_context(paper_id)
        save_to_csv(citations, filename)

    # Fallback to Google Scholar
    cites_id = search_paper_google_scholar(title)
    if cites_id:
        citations = get_citing_papers_google_scholar(cites_id)
        save_to_csv(citations, filename)
    else:
        print("Unable to find citations.")

def run():
    # === Paths ===
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    data_dir = os.path.join(base_dir, "data")
    METADATA_PATH = os.path.join(data_dir, "metadata.txt")

    # === Load publication title and year ===
    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
        publication_year = lines[-1]
        publication_title = " ".join(lines[:-1])

    output_csv = os.path.join(data_dir, 'scholarly_citations_output.csv')
    get_citations_by_title(publication_title, output_csv)

if __name__ == "__main__":
    run()