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

Publication Title: Heritable Human Genome Editing

Publication Year: 2020

<details>
  <summary>CTAs</summary>

Recommendation 1: No attempt to establish a pregnancy with a human em-
bryo that has undergone genome editing should proceed unless and until it has
been clearly established that it is possible to efficiently and reliably make precise
genomic changes without undesired changes in human embryos. These criteria
have not yet been met, and further research and review would be necessary to
meet them.
Recommendation 2: Extensive societal dialogue should be undertaken before
a country makes a decision on whether to permit clinical use of heritable human
genome editing (HHGE). The clinical use of HHGE raises not only scientific and
medical considerations but also societal and ethical issues that were beyond the
Commission’s charge.
Recommendation 3: It is not possible to define a responsible translational
pathway applicable across all possible uses of heritable human genome editing
(HHGE) because the uses, circumstances, and considerations differ widely, as do
the advances in fundamental knowledge that would be needed before different
types of uses could be considered feasible.
Clinical use of HHGE should proceed incrementally. At all times, there should
be clear thresholds on permitted uses, based on whether a responsible trans-
lational pathway can be and has been clearly defined for evaluating the safety
and efficacy of the use, and whether a country has decided to permit the use.
Recommendation 4: Initial uses of heritable human genome editing (HHGE),
should a country decide to permit them, should be limited to circumstances that
meet all of the following criteria:
1. the use of HHGE is limited to serious monogenic diseases; the Com-
mission defines a serious monogenic disease as one that causes severe
morbidity or premature death;
2. the use of HHGE is limited to changing a pathogenic genetic variant
known to be responsible for the serious monogenic disease to a sequence
that is common in the relevant population and that is known not to be
disease-causing;
3. no embryos without the disease-causing genotype will be subjected to
the process of genome editing and transfer, to ensure that no individuals
resulting from edited embryos were exposed to risks of HHGE without any
potential benefit; and
4. the use of HHGE is limited to situations in which prospective parents
(i) have no option for having a genetically-related child that does not
have the serious monogenic disease, because none of their embryos
would be genetically unaffected in the absence of genome editing; or
(ii) have extremely poor options, because the expected proportion of unaf-
fected ­ embryos would be unusually low, which the Commission defines as
continued
Copyright National Academy of Sciences. All rights reserved.
Heritable Human Genome Editing
4 HERITABLE HUMAN GENOME EDITING
BOX S-1 Continued
25 percent or less, and have attempted at least one cycle of preimplanta-
tion genetic testing without success.
Recommendation 5: Before any attempt to establish a pregnancy with an em-
bryo that has undergone genome editing, preclinical evidence must demonstrate
that heritable human genome editing (HHGE) can be performed with sufficiently
high efficiency and precision to be clinically useful. For any initial uses of HHGE,
preclinical evidence of safety and efficacy should be based on the study of a
significant cohort of edited human embryos and should demonstrate that the
process has the ability to generate and select, with high accuracy, suitable num-
bers of embryos that:
• have the intended edit(s) and no other modification at the target(s);
• lack additional variants introduced by the editing process at off-target
sites—that is, the total number of new genomic variants should not differ
significantly from that found in comparable unedited embryos;
• lack evidence of mosaicism introduced by the editing process;
• are of suitable clinical grade to establish a pregnancy; and
• have aneuploidy rates no higher than expected based on standard as-
sisted reproductive technology procedures.
Recommendation 6: Any proposal for initial clinical use of heritable human
genome editing should meet the criteria for preclinical evidence set forth in
­ Recommendation 5. A proposal for clinical use should also include plans to
evaluate human embryos prior to transfer using:
• developmental milestones until the blastocyst stage comparable with
standard in vitro fertilization practices; and
• a biopsy at the blastocyst stage that demonstrates
o the existence of the intended edit in all biopsied cells and no evidence
of unintended edits at the target locus; and
o no evidence of additional variants introduced by the editing process at
off-target sites.
If, after rigorous evaluation, a regulatory approval for embryo transfer is granted,
monitoring during a resulting pregnancy and long-term follow-up of resulting
children and adults is vital.
Recommendation 7: Research should continue into the development of meth-
ods to produce functional human gametes from cultured stem cells. The ability
to generate large numbers of such stem cell–derived gametes would provide a
further option for prospective parents to avoid the inheritance of disease through
the effi­ cient production, testing, and selection of embryos without the disease-
causing genotype. However, the use of such in vitro–derived gametes in repro-
ductive medicine raises distinct medical, ethical, and societal issues that must
be carefully evaluated, and such gametes without genome editing would need
to be approved for use in assisted reproductive technology before they could be
considered for clinical use of heritable human genome editing.
Copyright National Academy of Sciences. All rights reserved.
Heritable Human Genome Editing
SUMMARY 5
Recommendation 8: Any country in which the clinical use of heritable human
genome editing (HHGE) is being considered should have mechanisms and com-
petent regulatory bodies to ensure that all of the following conditions are met:
• individuals conducting HHGE-related activities, and their oversight bodies,
adhere to established principles of human rights, bioethics, and global
governance;
• the clinical pathway for HHGE incorporates best practices from related
technologies such as mitochondrial replacement techniques, preimplanta-
tion genetic testing, and somatic genome editing;
• decision making is informed by findings from independent international
assessments of progress in scientific research and the safety and efficacy
of HHGE, which indicate that the technologies are advanced to a point
that they could be considered for clinical use;
• prospective review of the science and ethics of any application to use
HHGE is diligently performed by an appropriate body or process, with
decisions made on a case-by-case basis;
• notice of proposed applications of HHGE being considered is provided by
an appropriate body;
• details of approved applications (including genetic condition, laboratory
procedures, laboratory or clinic where this will be done, and national bod-
ies providing oversight) are made publicly accessible, while protecting
family identities;
• detailed procedures and outcomes are published in peer-reviewed journals
to provide dissemination of knowledge that will advance the field;
• the norms of responsible scientific conduct by individual investigators and
laboratories are enforced;
• researchers and clinicians show leadership by organizing and participat-
ing in open international discussions on the coordination and sharing of
results of relevant scientific, clinical, ethical, and societal developments
impacting the assessment of HHGE’s safety, efficacy, long-term monitor-
ing, and societal acceptability;
• practice guidelines, standards, and policies for clinical uses of HHGE are
created and adopted prior to offering clinical use of HHGE; and
• reports of deviation from established guidelines are received and reviewed,
and sanctions are imposed where appropriate.
Recommendation 9: An International Scientific Advisory Panel (ISAP) should be
established with clear roles and responsibilities before any clinical use of heri-
table human genome editing (HHGE). The ISAP should have a diverse, multidis-
ciplinary membership and should include independent experts who can assess
scientific evidence of safety and efficacy of both genome editing and associated
assisted reproductive technologies.
The ISAP should:
• provide regular updates on advances in, and the evaluation of, the tech-
nologies that HHGE would depend on and recommend further research
developments that would be required to reach technical or translational
milestones;
continued
Copyright National Academy of Sciences. All rights reserved.
Heritable Human Genome Editing
6 HERITABLE HUMAN GENOME EDITING
BOX S-1 Continued
• assess whether preclinical requirements have been met for any circum-
stances in which HHGE may be considered for clinical use;
• review data on clinical outcomes from any regulated uses of HHGE and
advise on the scientific and clinical risks and potential benefits of possible
further applications; and
• provide input and advice on any responsible translational pathway
to the inter­ national body described in Recommendation 10, as well as
at the request of national regulators.
Recommendation 10: In order to proceed with applications of heritable human
genome editing (HHGE) that go beyond the translational pathway defined for
initial classes of use of HHGE, an international body with appropriate standing
and diverse expertise and experience should evaluate and make recommenda-
tions concerning any proposed new class of use. This international body should:
• clearly define each proposed new class of use and its limitations;
• enable and convene ongoing transparent discussions on the societal
­ issues surrounding the new class of use;
• make recommendations concerning whether it could be appropriate to
cross the threshold of permitting the new class of use; and
• provide a responsible translational pathway for the new class of use.
Recommendation 11: An international mechanism should be established by
which concerns about research or conduct of heritable human genome editing
that deviates from established guidelines or recommended standards can be
received, transmitted to relevant national authorities, and publicly disclosed.

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
