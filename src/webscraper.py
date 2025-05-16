import os
import re
import csv
import time
import shutil
import tempfile
import signal
import requests
import pandas as pd
from io import BytesIO
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from htmldate import find_date
import tldextract
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import chromedriver_autoinstaller
import google.generativeai as genai

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

# Constants
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
HEADLESS_OPTIONS = ["--headless=new", "--no-sandbox", "--disable-dev-shm-usage"]

# Ensure ChromeDriver is installed
chromedriver_autoinstaller.install()

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("Scraping timed out.")


# Utility Functions
def configure_chrome_options(headless=True):
    """Configure Chrome options for Selenium."""
    chrome_options = Options()
    if headless:
        for option in HEADLESS_OPTIONS:
            chrome_options.add_argument(option)
    chrome_options.add_argument(f"user-agent={USER_AGENT}")
    return chrome_options

def extract_base_domain(url):
    """Extract the base domain from a URL."""
    extracted = tldextract.extract(url)
    return f"{extracted.domain}.{extracted.suffix}"


def get_url_date_last_modified(mod_date, pub_date, source_date):
    """Determine the most relevant date for a URL."""
    custom_formats = ['%Y%b%d', '%Y%b', '%Y']

    for date in [mod_date, pub_date, source_date]:
        if pd.notna(date):
            # Try automatic parsing first
            date_obj = pd.to_datetime(date, errors='coerce')
            
            # If automatic parsing fails, try custom formats
            if pd.isna(date_obj):
                for fmt in custom_formats:
                    try:
                        date_obj = pd.to_datetime(date, format=fmt)
                        break
                    except (ValueError, TypeError):
                        continue
            if pd.notna(date_obj):
                return date_obj.date()
    
    return pd.NaT


# Web Scraping Functions
def scrape_text_with_selenium(url):
    """Scrape text from a webpage using Selenium."""
    chrome_options = configure_chrome_options()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        driver.set_page_load_timeout(30)
        driver.get(url)

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(3)  # Respect crawl-delay

        # Parse the page
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Remove unwanted elements that might contain irrelevant text
        for element in soup.select('nav, footer, .cookie-notice, .advertisement, script, style'):
            element.extract()

        # Find relevant content tags
        content_tags = soup.find_all(['p', 'h1', 'h2', 'h3', 'article', 'section', 'main'])

        # If we didn't find specific content tags, fall back to body text
        if not content_tags:
            content_tags = soup.find_all('body')

        # Extract and clean text
        page_text = " ".join(tag.get_text(strip=True) for tag in content_tags if tag.get_text(strip=True))

        current_url = driver.current_url

        if extract_base_domain(current_url) == "hhs.gov" or "ncbi.nlm.nih.gov" in current_url:
            mod_date = ""
            pub_date = ""
        else:
            mod_date = find_date(current_url, original_date=False)
            pub_date = find_date(current_url, original_date=True)

        return page_text, current_url, mod_date, pub_date
    except Exception as e:
        return f"Error scraping text: {e}", url, "", ""
    finally:
        driver.quit()

def solve_captcha_manually(url, timeout=60):
    options = Options()
    # Headless must be disabled to solve CAPTCHA
    # Create unique user data directory
    user_data_dir = tempfile.mkdtemp()
    options.add_argument(f"--user-data-dir={user_data_dir}")
    options.add_argument("--incognito")

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        print(f"Opening {url} — please solve CAPTCHA manually...")
        driver.get(url)

        while "Request Access" in driver.title or "captcha" in driver.page_source.lower():
            print("Waiting for CAPTCHA to be solved...")
            time.sleep(5)
        final_url = driver.current_url
        return final_url

    finally:
        try:
            driver.quit()
        except Exception:
            pass
        shutil.rmtree(user_data_dir, ignore_errors=True)

# PDF Handling
def download_pdf_with_selenium(url, download_folder="pdfs"):
    """Use Selenium to download a PDF."""
    os.makedirs(download_folder, exist_ok=True)
    chrome_options = configure_chrome_options()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        driver.get(url)
        time.sleep(10)  # Wait for the page to load
        selenium_cookies = driver.get_cookies()
        session = requests.Session()
        for cookie in selenium_cookies:
            session.cookies.set(cookie['name'], cookie['value'])

        response = session.get(url, headers={"User-Agent": USER_AGENT})
        response.raise_for_status()

        filename = os.path.basename(urlparse(url).path)
        if not filename.endswith(".pdf"):
            filename += ".pdf"

        pdf_path = os.path.join(download_folder, filename)
        with open(pdf_path, "wb") as f:
            f.write(response.content)

        print(f"PDF downloaded to: {pdf_path}")
        return pdf_path, url
    except Exception as e:
        print(f"Error downloading PDF: {e}")
        return None, url
    finally:
        driver.quit()


def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file using PyPDF2."""
    try:
        with open(pdf_path, "rb") as f:
            reader = PdfReader(f)
            return "".join(page.extract_text() for page in reader.pages[:10]).strip()
    except Exception as e:
        return f"Error extracting text from PDF: {e}"
    

def handle_pdf_url(url):
    """Handle scraping for PDF URLs."""
    try:
        pdf_path, final_url = download_pdf_with_selenium(url)
        if pdf_path:
            pdf_text = extract_text_from_pdf(pdf_path)
            return pdf_text, final_url, "", ""
        else:
            raise Exception("Error downloading PDF.")
    except Exception as e:
        error_message = f"Error processing PDF URL {url}: {e}"
        return error_message, url, "", ""


# PubMed Handling
def extract_pubmed_id(url):
    """Extract PubMed ID from a URL."""
    pubmed_match = re.search(r'pubmed\.ncbi\.nlm\.nih\.gov/(\d+)', url)
    if pubmed_match:
        return 'article', pubmed_match.group(1)

    time.sleep(0.1) 
    pmc_match = re.search(r'pmc\.ncbi\.nlm\.nih\.gov/articles/(PMC\d+)', url)
    if pmc_match:
        pmc_id = pmc_match.group(1)
        api_url = f"https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?tool=my_tool&email=shreyark@mit.edu&ids={pmc_id}&format=json"
        response = requests.get(api_url)
        if response.ok:
            data = response.json()
            records = data.get("records", [])
            if records and "pmid" in records[0]:
                return 'article', records[0]["pmid"]
    
    book_match = re.search(r'ncbi\.nlm\.nih\.gov/books/(NBK\d+)', url)
    if book_match:
        return 'book', book_match.group(1)
    
    return None, None


def fetch_pubmed_metadata_article(pmid):
    """Fetch metadata and article URL from PubMed using its API."""
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    api_key = os.getenv("NCBI_API_KEY")
    params = {"db": "pubmed", "id": pmid, "retmode": "xml", "api_key": api_key}

    time.sleep(0.1) 
    response = requests.get(base_url + "efetch.fcgi", params=params)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'xml')

    title = soup.find("ArticleTitle").get_text(strip=True) if soup.find("ArticleTitle") else "No title available."
    abstract = " ".join(abstract.get_text(strip=True) for abstract in soup.find_all("AbstractText")) or "No abstract available."
    pub_date = soup.find("PubDate").get_text(strip=True) if soup.find("PubDate") else ""
    mod_date = ""

    for pub_date_entry in soup.find_all("PubMedPubDate"):
        if pub_date_entry.get("PubStatus") == "revised":
            mod_date = pub_date_entry.get_text(strip=True)
            break
    pubmed_url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"

    return f"{title} {abstract}", pubmed_url, mod_date, pub_date


def fetch_pubmed_metadata_book(book_id):
    """Fetch metadata from PubMed Books."""
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    api_key = os.getenv("NCBI_API_KEY")
    params = {"db": "books", "id": book_id, "retmode": "xml", "api_key": api_key}

    response = requests.get(base_url + "efetch.fcgi", params=params)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'xml')

    title = soup.find("BookDocument").find("BookTitle").get_text(strip=True) if soup.find("BookTitle") else "No title available."
    abstract = soup.find("Abstract").get_text(strip=True) if soup.find("Abstract") else "No abstract available."

    book_url = f"https://www.ncbi.nlm.nih.gov/books/{book_id}/"
    return f"{title} {abstract}", book_url, "", ""  # Dates not usually included


# Federal Register Handling
def is_federal_register_url(url):
    """Check if URL is from the Federal Register."""
    return "federalregister.gov" in urlparse(url).netloc


def get_federal_register_content(url):
    """Fetch content from the Federal Register API."""
    try:
        doc_id = url.strip("/").split("/")[-1]
        api_url = f"https://www.federalregister.gov/api/v1/documents/{doc_id}.json"
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()

        title = data.get("title", "")
        body_html = data.get("body_html", "")
        body_text = BeautifulSoup(body_html, "html.parser").get_text(separator=" ", strip=True)
        pub_date = data.get("publication_date", "")
        mod_date = data.get("modified_date", "")

        return f"{title}\n\n{body_text}", url, mod_date, pub_date
    except Exception as e:
        return f"Error processing {url}: {e}", url, "", ""

def scrape_with_timeout(url, timeout=60):
    """Scrape a URL with a global timeout."""
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)  # Set the timeout

    try:
        return scrape_url(url)
    except TimeoutException:
        return f"Error: Timeout while scraping {url}", url, "", ""
    finally:
        signal.alarm(0)  # Disable the alarm

# Main Scraping Logic
def scrape_url(url):
    """Scrape content from a URL, handling special cases like PDFs and PubMed."""
    try:
        if '.pdf' in url.lower():
            return handle_pdf_url(url)

        format, pmid = extract_pubmed_id(url)
        if pmid:
            if format == 'article':
                return fetch_pubmed_metadata_article(pmid)
            else:
                return fetch_pubmed_metadata_book(pmid)

        if is_federal_register_url(url):
            resolved_url = solve_captcha_manually(url)
            return get_federal_register_content(resolved_url)

        return scrape_text_with_selenium(url)
    except Exception as e:
        return f"Error processing {url}: {e}", url, "", ""


# Main Pipeline
def run():
    """Run the scraping and Gemini pipeline."""
    # === Paths ===
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    input_csv = os.path.join(base_dir, 'data', 'cta_search_results.csv')
    output_csv = os.path.join(base_dir, 'data', 'webscrape_intermediate_output.csv')

    with open(input_csv, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    with open(output_csv, "w", newline='', encoding="utf-8") as output_file:
        writer = csv.writer(output_file)
        writer.writerow([
            "Title", "Publication Year", "Domain", "URL", "URL Title", "Extracted Content", "Recommendation",
            "URL Date Last Modified"
        ])

        for row in rows:
            title = row["Publication Title"]
            recommendation = row["CTA"]
            url_title = row["Title"]
            source_date = row["Source Date"]
            year = row['Publication Year']
            url = row["URL"]
            print(f"Processing: {url}")
            
            text, final_url, mod_date, pub_date = scrape_with_timeout(url)
            
            domain = extract_base_domain(final_url)
            last_modified_date = get_url_date_last_modified(mod_date, pub_date, source_date)
            if text.startswith("Error"):
                print(f"Error scraping {url}: {text}")
                writer.writerow([title, year, domain, url, url_title, "", recommendation, last_modified_date])
            else:
                preview = text[:100000]
                writer.writerow([title, year, domain, url, url_title, preview, recommendation, last_modified_date])

if __name__ == "__main__":
    run()