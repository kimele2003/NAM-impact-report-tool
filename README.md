# NAM-impact-report-tool

The **NAM Impact Report Tool** is a structured data pipeline that extracts, verifies, and summarizes the influence of public health and policy documents published by the [National Academy of Medicine (NAM)](https://nam.edu). It uses LLMs ([Gemini Flash 2.0](https://cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/2-0-flash)) and custom logic to identify calls to action (CTAs), evidence of policy impact, relevance explanations, and citations, all mapped to NAM recommendations and tracked at scale.

If you submit the analyze publication form below, in 10-30 minutes the output should automatically populate in the impact report dashboard. 
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

## Example Analyze Publication Form Input

Publication Title: The State of the U.S. Biomedical and Health Research Enterprise: Strategies for Achieving a Healthier America

Publication Year: 2024

<details>
  <summary>CTAs</summary>

Priority 1-1: A U.S. biomedical research enterprise advisory body, created by the President of the United States and Congress, to galvanize national leadership, develop a national strategic vision, and coordinate efforts and resources.
"Priority 1-2: This advisory body could:
    *   Be composed of leading scientists from a wide variety of disciplines, such as life, physical, social, and behavioral sciences; engineering; economics; and the humanities to ensure a convergence science approach to addressing all emerging needs;
    *   Engage with multiple relevant federal agencies;
    *   Be established with long terms;
    *   Be empowered to set national goals and benchmarks;
    *   Provide input on resource allocation that matches strategy;
    *   Consider, examine, and utilize global best practices in all aspects of its work, but especially as guidance for developing the national strategic vision;
    *   Include patients, caregivers, and members of the public to provide transparency and public engagement;
    *   Have clear, measurable goals and timelines;
    *   Coordinate with the National Economic Policy Council and the Domestic Policy Council to ensure the engagement of all relevant stakeholders; and
    *   Monitor their progress and report to Congress and the American public annually on their work."
"Priority 1-3: The advisory body’s national strategic vision could:
* Directly address the current fragmentation in funding and agenda-setting present in the U.S. biomedical research enterprise, in concert with the efforts proposed in Priorities 4-1 and 4-2. The national strategic vision cannot succeed without coordination and alignment of funding and agenda-setting, which, conversely, cannot be coordinated and aligned without the guidance of a national strategic vision. These priorities cannot be separated.
* Set priorities for the use of convergence science and implement a roadmap for bringing together relevant agencies and scientific disciplines to achieve this collaborative approach (see also Priority 4-2).
* Consider and propose funding to address:
    * Existing and emerging health challenges, including but not limited to infant and maternal mortality, women’s health concerns, deaths of despair, obesity, climate change, health disparities, diseases with pandemic potential, and diseases of aging;
    * Future health threats such as increasing risks of extreme heat and other natural disasters due to climate change and emerging or existing infectious diseases;
    * Public engagement in the entire U.S. biomedical research enterprise, but especially focused on increased participation in clinical trials;
    * Deteriorating public trust in science and medicine;
    * Prioritization and development of new and innovative research approaches to reduce and eliminate health disparities; and
    * The needs of the U.S. biomedical research enterprise workforce, including adjusting historical pathways to employment or tenure as emerging health challenges, approaches to science, or the needs of the American public change."
"Priority 2-1: A federally established national biomedical research funding collaborative, guided by best practices from existing international models, and federal determinations of how best to organize and allocate shared investments from the government, private sector, and philanthropy. The funding collaborative could be empowered to:
* Analyze successful existing models to develop best practices for the implementation of new methods for financing and accelerating biomedical research;
* Create a large-scale funding model to address the health challenges identified in the national strategic vision; and
* Develop new philanthropic collectives to encourage pooled, strategic gifts that can make a large impact."
Priority 2-2: Federally developed initiatives and funding strategies to specifically address the issue of the “funding valley of death” to translate promising basic research into breakthrough therapies, diagnostics, and treatments—helping to ensure that the full value of the U.S. biomedical research enterprise reaches all patients equitably.
"Priority 3-1: Federal prioritization of research that informs solutions for achieving health equity in the United States, including those focused on the social determinants of health, diversifying the workforce, and the U.S. biomedical research enterprise itself. These research areas could include:
*   Increasing trust in medicine, science, and the U.S. biomedical research enterprise itself;
*   Mitigating structural and systemic discrimination;
*   Delivering care to patients and the communities where they reside, using advances in implementation science to guide these solutions;
*   Improving the communication of scientific and medical information; and
*   Bolstering community engagement and effective bidirectional dialogue."
"Priority 3-2: Federal prioritization of research on the “health equity valley of death”—closing the last mile—to understand and eliminate barriers that are preventing the most vulnerable populations in the United States from receiving and accessing comprehensive, high-quality, culturally appropriate care. Specific research areas could include:
    *   The digital divide;
    *   Improving access to health care, specifically for individuals who cannot afford adequate or any insurance coverage;
    *   Transportation barriers;
    *   “Health care deserts,” or a lack of health care providers—primary and specialty—in a given geographic area;
    *   Improving trust in science, medicine, and practitioners of both;
    *   Providing care outside of clinics and hospitals to meet individuals where they are; and
    *   Reducing racism, sexism, and other discriminatory practices that may keep individuals from seeking care."
Priority 4-1: Federal requirement and facilitation of necessary and essential coordination across government agencies, especially the National Institutes of Health and the National Science Foundation, as well as external parties, to enable the use of convergence science, coordinate funding and strategy, adequately address the increasingly complex and interconnected health challenges facing the nation, and promote information sharing.
Priority 4-2: Federal promotion and use of convergence science in all appropriate projects receiving federal funding.
Priority 5: Steps by the federal government and Congress to increase the competitiveness of the U.S. biomedical research enterprise workforce..." (detailed components outlined above)


</details>

---

## Setup Instructions to Run Locally 

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
SERP_API_KEY=your_serp_api_key
GOOGLE_CSE_ID=your_google_custom_search_engine_id
GOOGLE_API_KEY=your_google_api_key
NCBI_API_KEY=your_ncbi_api_key

```
---

## How to Run
First, submit the [Analyze Publication Form](https://airtable.com/appUVmalqSjgpivpw/pagw5kixW9UnGvN5k/form)

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
