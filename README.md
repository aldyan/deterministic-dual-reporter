# deterministic-dual-reporter

[![CI](https://github.com/aldyansaputra/deterministic-dual-reporter/actions/workflows/ci.yml/badge.svg)](https://github.com/aldyansaputra/deterministic-dual-reporter)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A deterministic, brand-agnostic test execution compiler that transforms JSON test execution manifests into executive Word (`.docx`) reports and responsive, self-contained HTML5 telemetry dashboards. 

Every execution artifact (HTTP payloads, logs, SQL results, screenshots) is stamped with an immutable **SHA-256 hash**, eliminating unverifiable test claims and preventing false-positive pass rates in continuous integration and automated test cycles.

---

## Key Capabilities

* **Dual-Output Compilation:** Produces both an interactive 5-tab responsive HTML5 dashboard and a formal executive Word document (`.docx`) from a single JSON test manifest.
* **Cryptographic Evidence Hashing:** Stamped SHA-256 integrity hashes on all supporting evidence to guarantee auditability and tamper-proof verification.
* **Strict 4-Tier Defect Taxonomy:** Enforces a single, non-inflated defect classification:
  * `BLOCKER`: Service, build, or critical workflow completely inoperable.
  * `MAJOR`: Primary business functionality broken with no workaround.
  * `MINOR`: Non-blocking edge case or secondary feature defect.
  * `TRIVIAL`: Cosmetic or minor layout misalignment.
* **Zero External Template Dependency:** Generates pristine, professionally formatted Word documents directly via OpenXML without relying on brittle external `.dotx` files.
* **Self-Contained HTML5 Telemetry:** The generated HTML report requires no external CDNs, bundlers, or heavy JavaScript frameworks.

---

## Architecture Overview

```
JSON Test Manifest (test_cases, defects, evidences)
                       │
                       ▼
          [TestRunManifest Parser]
         /                        \\
        ▼                          ▼
 [HTML5 Telemetry Builder]    [DOCX Executive Builder]
        │                                  │
        ▼                                  ▼
 reports/<run_id>.html        reports/<run_id>.docx
```

---

## Installation

```bash
# Clone the repository
git clone https://github.com/aldyansaputra/deterministic-dual-reporter.git
cd deterministic-dual-reporter

# Install with pip
pip install .

# Or using uv
uv sync
```

---

## Quickstart (CLI)

Compile the bundled example manifest:

```bash
# Generate both HTML and DOCX reports
dual-reporter examples/sample_manifest.json --out-dir reports

# Generate HTML dashboard only
dual-reporter examples/sample_manifest.json --out-dir reports --format html

# Generate DOCX document only
dual-reporter examples/sample_manifest.json --out-dir reports --format docx
```

Output:
```text
Loaded Test Run: RUN-2026-E2E-09 (Enterprise Core Gateway & Settlement Engine)
Cases: 10 | Passed: 8 | Failed: 2 | Defects: 2
-> Generated HTML Dashboard: /path/to/reports/RUN-2026-E2E-09_enterprise_core_gateway_&_settlement_engine.html
-> Generated DOCX Report:    /path/to/reports/RUN-2026-E2E-09_enterprise_core_gateway_&_settlement_engine.docx
Compilation complete. 100% SHA-256 evidence parity maintained.
```

---

## Python API Usage

You can embed the reporter directly into custom automation frameworks (e.g., Pytest hooks, Playwright runners, or autonomous agent executors):

```python
from dual_reporter import TestRunManifest, render_html_report, build_docx_report

# Load or construct manifest data
manifest_data = {
    "run_id": "RUN-2026-001",
    "system_under_test": "Core Banking Gateway",
    "environment": "SIT / Staging",
    "executed_at": "2026-10-20 14:00:00 UTC",
    "verification_lead": "Aldyan Saputra",
    "test_cases": [
        {
            "id": "TC-01",
            "component": "Auth",
            "title": "OAuth2 Token Issuance",
            "technique": "HAPPY_PATH",
            "status": "PASSED",
            "duration_ms": 120
        }
    ],
    "defects": [],
    "evidences": []
}

manifest = TestRunManifest.from_dict(manifest_data)

# Generate HTML
html_content = render_html_report(manifest)
with open("reports/report.html", "w", encoding="utf-8") as f:
    f.write(html_content)

# Generate DOCX
build_docx_report(manifest, "reports/report.docx")
```

---

## Test Manifest Schema

Manifests are simple, declarative JSON files:

```json
{
  "run_id": "RUN-2026-E2E-09",
  "system_under_test": "System Name",
  "environment": "STAGING / SIT",
  "executed_at": "2026-10-20 14:00:00 UTC",
  "verification_lead": "QA Lead Name",
  "test_cases": [
    {
      "id": "TC-001",
      "component": "Gateway",
      "title": "Scenario description",
      "technique": "BOUNDARY_VALUE_ANALYSIS",
      "status": "PASSED",
      "duration_ms": 150,
      "evidence_id": "EV-01"
    }
  ],
  "defects": [
    {
      "id": "DEF-01",
      "title": "Observed failure title",
      "severity": "MAJOR",
      "steps": "1. Step one\\n2. Step two",
      "expected_result": "Clean execution",
      "actual_result": "Exception thrown",
      "root_cause": "Race condition in worker",
      "evidence_ref": "EV-01"
    }
  ],
  "evidences": [
    {
      "id": "EV-01",
      "name": "payload.json",
      "evidence_type": "HTTP_PAYLOAD",
      "content_or_path": "{\"status\": \"error\"}"
    }
  ]
}
```

---

## License

MIT License. Copyright (c) 2026 Aldyan Saputra.
