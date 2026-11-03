# AI-Powered Financial Risk Intelligence

A research platform for testing whether changes in corporate risk disclosures add predictive information about subsequent financial deterioration beyond traditional financial ratios.

## Phase 1 status

Implemented in this phase: a minimal SEC EDGAR Company Facts client, project/development configuration, mocked client tests, and GitHub Actions checks. Later roadmap items remain planned; no model results or research findings are claimed.

## Research objective

The core question is whether changes in corporate risk disclosures provide incremental predictive information about subsequent financial deterioration beyond traditional financial ratios. The project will preserve filing dates and data provenance, avoid look-ahead bias, and compare financial, text-derived, and combined signals using chronological evaluation.

## Architecture

```text
SEC EDGAR Company Facts + historical 10-K filings
                    |
          ingestion and provenance
                    |
       financial features + disclosure text
                    |
  chronological model evaluation and calibration
                    |
 evidence retrieval and source-grounded explanations
                    |
             Streamlit research dashboard
```

The current `src/financial_risk_intelligence/sec/company_facts.py` module provides the first ingestion component. The other components are roadmap items and are not implemented yet.

## Installation

Requires Python 3.12 or newer.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
python -m pip install -e '.[dev]'
cp .env.example .env
```

Set `SEC_USER_AGENT` in your environment (or `.env`) to an application identifier with a contact email, following SEC guidance. This project does not load `.env` automatically; export the values before running Python.

## SEC Company Facts client

```python
from financial_risk_intelligence.sec import CompanyFactsClient

client = CompanyFactsClient()  # reads SEC_USER_AGENT and SEC_API_TIMEOUT
facts = client.get_company_facts("320193")  # accepts CIK digits, pads to 10 digits
```

The client returns the SEC JSON document, raises on HTTP errors or unexpected response shape, and accepts an injectable `requests.Session` for tests or caller-managed connection reuse. It does not cache, retry, or download filing documents in Phase 1.

## Development

```bash
ruff check .
pytest
```

GitHub Actions runs Ruff and pytest on pushes and pull requests.

## Development roadmap

1. **Phase 1 — foundation and SEC Company Facts:** project structure, configuration, CI, and mocked API client tests. (Current phase.)
2. **Phase 2 — SEC ingestion:** historical 10-K metadata and filing text with dates, provenance, and polite API access.
3. **Phase 3 — financial analytics:** fundamentals and time-aware growth, margin, leverage, liquidity, and cash-flow features.
4. **Phase 4 — disclosure NLP:** extract Risk Factors and MD&A and derive disclosure-change signals.
5. **Phase 5 — research evaluation:** financial-only, NLP-only, and combined logistic regression/XGBoost comparisons using chronological validation, calibration, appropriate metrics, uncertainty, and leakage controls.
6. **Phase 6 — Narrative–Financial Divergence Score:** define an interpretable score and evaluate its incremental usefulness.
7. **Phase 7 — evidence-grounded RAG and Streamlit dashboard:** retrieve filing evidence with traceable citations and display financial trends, disclosure changes, and model outputs.

Raw filings, credentials, and generated datasets should remain outside version control. Experimental results will be reported only after they are produced and evaluated.
