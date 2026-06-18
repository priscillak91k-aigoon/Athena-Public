# Hawkeye v5.0: Agent Setup & Verification Guide

This guide is a step-by-step walkthrough for setting up and running the **Hawkeye v5.0** Building Plan Auditor agent. 

---

## 1. System Overview

Hawkeye audits architectural plans and specifications for NZ Building Code (NZBC) compliance before they are submitted to the local council (BCA). It performs the following pipeline:

1. **OCR & Tiling**: Renders drawings into images for visual parsing.
2. **Fact Graph**: Builds a dependency graph between plans, specs, and engineering documents.
3. **Compliance Solver**: Solves bracing demands (NZS 3604) and thermal envelope insulation minimums (H1/AS1).
4. **Adversary Simulation**: Simulates a pedantic council processing officer using a local LLM to predict RFI (Request for Information) items.
5. **Dashboard Compiler**: Renders a premium, filterable HTML discrepancy report.

---

## 2. Prerequisites & Installation

Hawkeye runs on Python 3 and requires a few basic libraries for PDF processing and image rendering.

### Step 1: Install Python Dependencies
Open your terminal or command prompt and run:
```bash
pip install pymupdf pillow
```

### Step 2: Configure the Local LLM Endpoint (Optional)
The adversary simulator (`hawkeye_v5_adversary.py`) connects to a local LLM running on the ATOM server or Ollama.
* **Default Endpoint**: `http://localhost:8000/v1/chat/completions`
* **Default Model**: `deepseek-ai/DeepSeek-R1-Distill-Llama-70B-FP8` (falls back to Llama-3 or Llama-2 if not present).
* *Note*: If the LLM service is offline, the script will skip LLM auditing and compile the deterministic code checks.

---

## 3. Directory Layout

Ensure your project workspace contains these folders and files:

```text
Athena-Public/
├── artifacts/
│   └── (Interactive HTML and JSON reports will generate here)
├── docs/
│   └── HAWKEYE_AGENT_GUIDE.md (This guide)
├── scripts/
│   ├── hawkeye_v5_ocr.py
│   ├── hawkeye_v5_graph.py
│   ├── hawkeye_v5_compliance.py
│   ├── hawkeye_v5_adversary.py
│   └── hawkeye_v5_verify.py
└── vault/
    └── regulatory/
        └── nzbc/
            └── NZ_Consent_Master_Checksheet.md
```

---

## 4. How to Run the Verification Audit

To execute the test suite (which audits the historical sets for 675 Portobello Road, 64 Lynn Street, and 12 Bedford Parade), run the following command from the root of the `Athena-Public` folder:

```bash
python scripts/hawkeye_v5_verify.py
```

### Console Output
You should see output similar to this:
```text
--- Auditing 675 Portobello Road ---
Reading plans PDF...
Portobello audit complete. Flagged 8 RFI hazards.

--- Auditing 64 Lynn Street ---
Reading Lynn St RFI file...
Lynn Street audit complete. Flagged 3 RFI hazards.

--- Auditing 12 Bedford Parade (Change of Use) ---
Checking H1 compliance for suspended concrete floor...
Running comparative NZS 3604 bracing demand solver...
  - Dunedin (Z=0.13): 85.0 BUs
  - Wellington (Z=0.30): 180.0 BUs
Bedford Parade audit complete. Flagged 2 RFI hazards.

--- Compiling Interactive HTML Discrepancy Report ---
Interactive HTML Discrepancy Report saved to: file:///C:/Users/sarah/Athena-Public/artifacts/hawkeye_v5_audit_report.html
```

---

## 5. Reviewing the Results

Once the script runs successfully, open the generated dashboard to inspect the findings:

1. Navigate to: `C:/Users/sarah/Athena-Public/artifacts/`
2. Open [hawkeye_v5_audit_report.html](file:///c:/Users/sarah/Athena-Public/artifacts/hawkeye_v5_audit_report.html) in any web browser.
3. **Dashboard Controls**:
   * Filter results by project (Portobello, Lynn St, Bedford Parade).
   * Filter findings by severity (Critical vs. Medium).
   * View the structural bracing comparison (Dunedin $Z=0.13$ vs. Wellington $Z=0.30$).
   * Click **View Checksheet** to review the national 43-section NZBC checksheet database.
