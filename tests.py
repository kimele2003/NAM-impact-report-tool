import sys
from datetime import date
import json
import types
import pytest
import pandas as pd

# Ensure project root is importable
sys.path.insert(0, "./")

from src import generate_links, extract_ctas, webscraper, fetch_input


def test_extract_base_domain_various():
    assert webscraper.extract_base_domain("https://sub.example.co.uk/path") == "example.co.uk"
    assert webscraper.extract_base_domain("https://www.hhs.gov/some/page") == "hhs.gov"
    assert webscraper.extract_base_domain("https://ncbi.nlm.nih.gov/articles/PMC123456/") == "ncbi.nlm.nih.gov"


def test_get_url_date_last_modified_parsing():
    # ISO timestamp should be parsed to a date
    d = webscraper.get_url_date_last_modified("2022-04-05T12:00:00Z", "", "")
    assert isinstance(d, date)
    assert d == date(2022, 4, 5)


def test_extract_cta_blocks_text():
    sample = (
        "Recommendation 1: Increase funding for research.\n"
        "Recommendation 2: Improve data sharing.\n\n"
        "A-3. Strengthen oversight and monitoring.\n"
        "1. Support community engagement.\n"
        "2. Expand training.\n"
    )
    blocks = generate_links.extract_cta_blocks(sample)
    # Should find the Recommendation blocks and the A-3/numbered blocks
    assert any("Recommendation 1" in b for b in blocks)
    assert any("Recommendation 2" in b for b in blocks)
    assert any("A-3" in b or "A-3." in b for b in blocks)


def test_count_ctas_in_output_matches():
    sample = "Recommendation 1: Do X.\nPriority 2: Do Y.\nRecommendation 3: Do Z."
    cnt = extract_ctas.count_ctas_in_output(sample)
    assert cnt == 3


def test_extract_pubmed_id_patterns():
    fmt, pmid = webscraper.extract_pubmed_id("https://pubmed.ncbi.nlm.nih.gov/12345678/")
    assert fmt == "article"
    assert pmid == "12345678"

    fmt2, book_id = webscraper.extract_pubmed_id("https://www.ncbi.nlm.nih.gov/books/NBK447260/")
    assert fmt2 == "book"
    assert book_id == "NBK447260"


def test_is_federal_register_url():
    assert webscraper.is_federal_register_url("https://www.federalregister.gov/documents/2021/01/01/12345/example")
    assert not webscraper.is_federal_register_url("https://www.example.com/page")


def test_generate_search_queries_for_ctas_mocked(monkeypatch):
    sample_ctas = ["CTA 1 text", "CTA 2 text"]

    class DummyResponse:
        def __init__(self, text):
            self.text = text

    def fake_generate_content(prompt):
        # Return a well-formed Gemini-style response
        return DummyResponse(
            'CTA: Sample CTA\nStakeholders: Stake A; Stake B\nSearch Queries:\n- site:nih.gov sample query one\n- site:who.int sample query two\n- site:nytimes.com sample query three'
        )

    monkeypatch.setattr(generate_links, "model", types.SimpleNamespace(generate_content=fake_generate_content))

    outputs = generate_links.generate_search_queries_for_ctas(sample_ctas)
    assert isinstance(outputs, list)
    assert len(outputs) == 2
    assert "Stakeholders:" in outputs[0]


def test_compile_results_with_mocked_search(monkeypatch):
    # Prepare a single CTA block in the expected text format
    block = (
        'CTA: Improve data sharing\nStakeholders: NIH, HHS\nSearch Queries:\n- site:nih.gov data sharing policy\n- site:hhs.gov data sharing guidance'
    )

    # Mock search_google 
    def fake_search_google(query, api_key, cse_id):
        return [
            ("Title A", "https://example.gov/docA", "Snippet A", "2021-05-01"),
            ("Title B", "https://example.org/docB", "Snippet B", "2020-12-12"),
        ]

    monkeypatch.setattr(generate_links, "search_google", fake_search_google)

    df = generate_links.compile_results([block], api_key="KEY", cse_id="CSE", publication_title="Pub", publication_year="2025")
    assert isinstance(df, pd.DataFrame)
    # Two queries are sampled per CTA and each query returns 2 results -> up to 4 rows
    assert len(df) >= 1
    assert set(df.columns).issuperset({"Publication Title", "CTA", "Query", "Title", "URL"})


@pytest.fixture
def tmp_project_dir(tmp_path):
    project = tmp_path / "project"
    src = project / "src"
    data = project / "data"
    src.mkdir(parents=True)
    data.mkdir()
    return project, src, data


def test_fetch_input_airtable_mock(monkeypatch, tmp_project_dir):
    project, src, data = tmp_project_dir

    # Prepare a mock table and Api to simulate Airtable behavior
    updates = []

    class MockTable:
        def all(self, sort=None):
            return [
                {
                    "id": "rec123",
                    "fields": {
                        "CTAs": "Example CTA from Airtable",
                        "Processed": False,
                        "Publication Title": "Test Pub",
                        "Publication Year": "2024",
                    },
                }
            ]

        def update(self, record_id, data):
            updates.append((record_id, data))

    class MockApi:
        def __init__(self, pat):
            pass

        def table(self, base_id, table_name):
            return MockTable()

    # Monkeypatch Api in fetch_input module
    monkeypatch.setattr(fetch_input, "Api", MockApi)

    # Point module __file__ to the tmp project src so run() writes into project/data
    fake_module_file = src / "fetch_input.py"
    fetch_input.__file__ = str(fake_module_file)

    # Run the function
    fetch_input.run()

    # Verify files were created in the project data dir
    cta_path = data / "cta_input.txt"
    meta_path = data / "metadata.txt"

    assert cta_path.exists()
    assert meta_path.exists()
    # Ensure Airtable update was called
    assert any(u[0] == "rec123" for u in updates)


def test_generate_exec_summary_and_upload(monkeypatch, tmp_project_dir):
    import types
    from src import export_exec_summary

    project, src, data = tmp_project_dir

    # Point module __file__ so it looks for data in project/data
    export_exec_summary.__file__ = str(src / "export_exec_summary.py")

    # Create minimal CSV files that pandas can read inside project/data
    reco_csv = data / "webscrape_output.csv"
    cite_csv = data / "scholarly_citations_output.csv"
    reco_csv.write_text("Title,Publication Year,Domain,URL,URL Title,Extracted Content,Recommendation,URL Date Last Modified\n")
    cite_csv.write_text("Citation,Source\n")

    # Create CTA input excerpt and metadata
    cta_input = data / "cta_input.txt"
    meta = data / "metadata.txt"
    cta_input.write_text("This is a short excerpt describing policy recommendations and evidence of impact.")
    meta.write_text("Test Publication Title\n2025")

    # Mock the Gemini model to return a stylized response including markdown that should be cleaned
    class DummyResp:
        def __init__(self, text):
            self.text = text

    fake_text = (
        "**1. Overview of the Report**\n- Title: *Test Publication Title*\n"
        "A concise summary.\n\n"
        "**2. Evidence of Recommendations**\n- Some evidence found.\n\n"
        "**3. Publication Citations & Scholarly Uptake**\n- Cited by journals."
    )

    monkeypatch.setattr(export_exec_summary, "model", types.SimpleNamespace(generate_content=lambda prompt: DummyResp(fake_text)))

    # Mock Airtable Table to capture create/update
    created = {}

    class MockTable:
        def __init__(self, pat, base_id, table_name):
            self.table_name = table_name

        def all(self):
            return []

        def create(self, data):
            created['data'] = data

        def update(self, rec_id, data):
            created['updated'] = (rec_id, data)

    monkeypatch.setattr(export_exec_summary, "Table", MockTable)

    # Run the module's run() which will call the mocked model and Table
    export_exec_summary.run()

    # Validate that an Executive Summary was created and markdown removed
    assert 'data' in created
    assert created['data']["Publication Title"] == "Test Publication Title"
    summary_text = created['data']["Executive Summary"]
    # Should not contain markdown bold or asterisks
    assert "**" not in summary_text
    assert "*" not in summary_text


def test_handle_pdf_url_hhs():
    # HHS PDF URLs are intentionally blocked by the handler
    from src import webscraper

    text, final_url, mod_date, pub_date = webscraper.handle_pdf_url("https://www.hhs.gov/some/doc.pdf")
    assert "Error processing PDF URL" in text
    assert final_url == "https://www.hhs.gov/some/doc.pdf"


def test_scrape_with_timeout_times_out(monkeypatch):
    from src import webscraper
    import time

    def slow_scrape(url):
        time.sleep(0.15)
        return ("ok", url, "", "")

    monkeypatch.setattr(webscraper, "scrape_url", slow_scrape)
    result = webscraper.scrape_with_timeout("https://example.com", timeout=0.05)
    assert isinstance(result, tuple)
    assert result[0].startswith("Error: Timeout while scraping")


def test_compile_results_no_queries_returns_empty(monkeypatch):
    from src import generate_links

    block = "CTA: Something\nStakeholders: None\n"  # no Search Queries section
    df = generate_links.compile_results([block], api_key="K", cse_id="C")
    assert hasattr(df, "shape")
    assert df.shape[0] == 0


def test_extract_text_from_pdf_mocked(tmp_path, monkeypatch):
    from src import webscraper

    # Create a dummy pdf file (can be empty because we mock PdfReader)
    pdf_file = tmp_path / "dummy.pdf"
    pdf_file.write_bytes(b"%PDF-1.4\n%EOF")

    class DummyPage:
        def __init__(self, text):
            self._text = text

        def extract_text(self):
            return self._text

    class DummyReader:
        def __init__(self, fh):
            self.pages = [DummyPage("Page1 text."), DummyPage("Page2 text.")]

    monkeypatch.setattr(webscraper, "PdfReader", DummyReader)

    text = webscraper.extract_text_from_pdf(str(pdf_file))
    assert "Page1 text." in text
    assert "Page2 text." in text
