# AI-Powered Contract Clause Analysis

A local Streamlit prototype that extracts PDF/DOCX text, detects clause-category evidence using transparent keyword rules, compares findings to a checklist, stores review records in SQLite, and exports CSV/JSON/PDF reports. It assists human reviewers and is **not legal advice**.

## Requirements and implementation notes

The separate requirements PDF named in the pasted brief was not present in the provided files. This implementation follows the detailed pasted requirements. It includes all 15 requested categories, evidence excerpts, page references where available, conservative unreadable-page handling, checklist comparison, review notes/decisions, database deletion, and reports. Scanned-page OCR, secure multi-user authentication, robust assignment workflow, and automated retention purging are not implemented. DOCX references use paragraph positions because DOCX pagination is not stable. Synthetic PDF and DOCX sample contracts are included in `sample_data/`, along with the source text and a generated example report.

## Setup

Python 3.10+ recommended.

### Windows PowerShell
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
pytest -q
streamlit run app.py
```

### Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
pytest -q
streamlit run app.py
```

The SQLite database initializes at `data/app.db`. Set `DB_PATH` to override. The upload size limit defaults to 25 MB (`MAX_UPLOAD_MB`).

## Workflow

1. Open **Checklist Management** and edit categories or upload JSON in the documented array format. `sample_data/sample_checklist.json` is an example.
2. In **Upload Contract**, provide PDF/DOCX and metadata, then analyze.
3. Inspect evidence and comparison results in their navigation sections.
4. Add reviewer decisions/annotations in **Human Review**.
5. Export CSV, JSON, or PDF in **Reports and Export**; use delete there to remove the stored record and annotations.

Synthetic demo files are `sample_data/sample_contract.pdf` and `sample_data/sample_contract.docx`, with source text in `sample_data/sample_contract.txt`. They intentionally contain a payment wording deviation, potentially broad liability language, and no data-protection clause. Example exports are in `sample_data/example_report.pdf` and `sample_data/example_report.json`. No real contract or personal data is included.

## AI configuration

AI is disabled by default. Optional compatible OpenAI-style endpoint settings are `AI_ENABLED=true`, `AI_BASE_URL`, `AI_API_KEY`, and `AI_MODEL` in `.env`. Do not configure an external provider unless explicitly approved for the document data. AI explanation adapter falls back on provider errors. Core app analysis currently remains rule-based; it does not automatically send uploaded content to the provider.

## Data and security

Original uploads are processed in memory and not retained. Extracted text and review analysis are stored in local SQLite. This demo has no authentication, encryption at rest, or multi-user access controls; local file permissions and machine access are the operator's responsibility. Do not deploy publicly or use confidential documents without an appropriately reviewed security design. Delete records via Reports and Export. Retention days are informational only; scheduled purging is not implemented. SQL uses parameterized values and foreign-key cascade for annotations.

## Limitations

Keyword rules can miss relevant clauses or produce false matches; no legal meaning is inferred. Similarity comparisons are a simple text heuristic, not semantic/legal equivalence. Unreadable PDF pages are marked, and missing terms become human review rather than missing. OCR is not included. PDF and DOCX extraction varies with file construction. No arbitrary legal risk score is generated. Authentication, reviewer assignments, and automatic retention enforcement are not implemented.

## Troubleshooting

- `ModuleNotFoundError`: activate the virtual environment and reinstall requirements.
- PDF import/read error: confirm it is a valid PDF; password-protected files may fail.
- No clause matches: inspect extracted text and use an approved checklist; rules rely on keywords.
- AI settings have no effect on core classification: external AI use is deliberately not in the analysis path.
- SQLite locked: close other app instances; keep database on a local filesystem.

## Tests

Run `pytest -q`. Tests use synthetic in-memory PDF/DOCX and temporary SQLite files. The suite covers extraction, clause evidence, unreadable handling, database notes/deletion, exports, and invalid types.
