# NAM-impact-report-tool

The **NAM Impact Report Tool** is a structured data pipeline that extracts, verifies, and summarizes the influence of public health and policy documents published by the [National Academy of Medicine (NAM)](https://nam.edu). It uses LLMs ([Gemini Flash 2.0](https://cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/2-0-flash)) and custom logic to identify calls to action (CTAs), evidence of policy impact, relevance explanations, and citations, all mapped to NAM recommendations and tracked at scale.

- [Analyze Publication Form](https://airtable.com/appUVmalqSjgpivpw/pagw5kixW9UnGvN5k/form)
- [Impact Report Dashboard](https://airtable.com/appUVmalqSjgpivpw/pagPfSvIvBE09uD7M?j0m9a=sfs15iSINXSiorjhg&yPOWP=sfslSEmSIj7BjIFPl&JSpSM=sfsVypdB0YvRhTfWI)

---

## Key Features

- LLM-based content extraction from long-form [policy PDFs](https://nam.edu/resources/publications/)
- Evidence verification using trusted sources (e.g., WHO, NIH, NYTimes, PubMed)
- Executive summary generation tailored for non-technical stakeholders
- Airtable integration for centralized, collaborative insight tracking
- Modular pipeline with batch support and structured output

---

## Setup Instructions

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/NAM-impact-report-tool.git
cd NAM-impact-report-tool
```

### 2. Create and activate a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create a ```.env``` file with your API keys
```
AIRTABLE_PAT=your_airtable_api_key
AIRTABLE_BASE_ID=your_airtable_base_id
GEMINI_API_KEY=your_google_gemini_api_key
```
---

## How to Run

### Run the full pipeline
```
python3 -m src.main
```
---
## Airtable Integration

The tool connects to Airtable via the ```pyairtable``` SDK and uploads data to:

- ```Recommendations``` table: impact tracking insights for each Call-to-Action (CTA)
- ```Scholarly Citations``` table: records where NAM publications are cited in academic or policy-related contexts
- ```Executive Summaries``` table: policy-facing plain-language summaries

---

## Data Sources

This tool draws from and verifies against trusted sources such as:

- [NIH.gov](https://www.nih.gov)
- [USA.gov](https://www.usa.gov)
- [HHS.gov](https://www.hhs.gov)
- [WHO.int](https://www.who.int)
- [PubMed](https://pubmed.ncbi.nlm.nih.gov)
- [NYTimes.com](https://www.nytimes.com)

---

## Contributors

- Elenna Kim (MIT CS undergrad)
- Shreya Kalyan (MIT CS undergrad)
- Riya Patel (MIT MBA)
- Mahati Vavilala (MIT MBA)