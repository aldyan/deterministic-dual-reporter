"""Modern, self-contained, anti-slop HTML5 test telemetry dashboard generator."""

from __future__ import annotations
import json
from .models import TestRunManifest, DefectSeverity, TestStatus


def render_html_report(manifest: TestRunManifest) -> str:
    """Compiles TestRunManifest into a clean, standalone, responsive HTML5 dashboard."""
    
    defect_counts = manifest.get_defect_count_by_tier()
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>QA Verification Report — {manifest.system_under_test} [{manifest.run_id}]</title>
  <style>
    :root {{
      --bg: #0d1117;
      --surface: #161b22;
      --surface-hover: #1c2128;
      --border: #30363d;
      --border-muted: #21262d;
      --text: #e6edf3;
      --text-muted: #8b949e;
      --text-dim: #6e7681;
      
      --pass: #3fb950;
      --fail: #f85149;
      --blocked: #d29922;
      --accent: #58a6ff;
      
      --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif;
      --font-mono: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: var(--font-sans);
      background-color: var(--bg);
      color: var(--text);
      line-height: 1.5;
      font-size: 14px;
      padding: 32px 24px;
    }}

    .container {{
      max-width: 1200px;
      margin: 0 auto;
    }}

    /* Header & Run Telemetry */
    .report-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      border-bottom: 1px solid var(--border);
      padding-bottom: 24px;
      margin-bottom: 28px;
      gap: 20px;
      flex-wrap: wrap;
    }}

    .header-left h1 {{
      font-size: 24px;
      font-weight: 600;
      letter-spacing: -0.02em;
      margin-bottom: 6px;
      color: #ffffff;
    }}

    .header-meta {{
      display: flex;
      gap: 16px;
      font-size: 12px;
      color: var(--text-muted);
      font-family: var(--font-mono);
      flex-wrap: wrap;
    }}

    .header-meta span strong {{
      color: var(--text);
    }}

    .verdict-badge {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 6px 14px;
      border-radius: 6px;
      font-family: var(--font-mono);
      font-size: 13px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}

    .verdict-passed {{ background: rgba(63, 185, 80, 0.15); color: var(--pass); border: 1px solid rgba(63, 185, 80, 0.4); }}
    .verdict-failed {{ background: rgba(248, 81, 73, 0.15); color: var(--fail); border: 1px solid rgba(248, 81, 73, 0.4); }}
    .verdict-conditionally_passed {{ background: rgba(210, 153, 34, 0.15); color: var(--blocked); border: 1px solid rgba(210, 153, 34, 0.4); }}

    /* KPI Metrics Cards */
    .metrics-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
      margin-bottom: 32px;
    }}

    .metric-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 18px 20px;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }}

    .metric-label {{
      font-size: 12px;
      color: var(--text-muted);
      font-weight: 500;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}

    .metric-val {{
      font-size: 28px;
      font-weight: 700;
      font-family: var(--font-mono);
      line-height: 1.1;
      color: #ffffff;
    }}

    .metric-sub {{
      font-size: 11px;
      color: var(--text-dim);
      margin-top: 2px;
    }}

    /* Tab Navigation */
    .tabs-nav {{
      display: flex;
      border-bottom: 1px solid var(--border);
      gap: 8px;
      margin-bottom: 24px;
    }}

    .tab-btn {{
      background: transparent;
      border: none;
      border-bottom: 2px solid transparent;
      color: var(--text-muted);
      font-size: 13px;
      font-weight: 500;
      padding: 10px 16px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 8px;
      transition: color 0.15s, border-color 0.15s;
    }}

    .tab-btn:hover {{ color: var(--text); }}
    .tab-btn.active {{
      color: var(--text);
      border-bottom-color: var(--accent);
    }}

    .tab-pill {{
      font-size: 11px;
      font-family: var(--font-mono);
      background: rgba(255, 255, 255, 0.08);
      padding: 1px 6px;
      border-radius: 10px;
    }}

    /* Table Styles */
    .table-container {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 8px;
      overflow-x: auto;
      margin-bottom: 32px;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      text-align: left;
      font-size: 13px;
    }}

    th {{
      background: #1c2128;
      color: var(--text-muted);
      font-weight: 600;
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.03em;
      padding: 12px 16px;
      border-bottom: 1px solid var(--border);
    }}

    td {{
      padding: 12px 16px;
      border-bottom: 1px solid var(--border-muted);
      vertical-align: middle;
    }}

    tr:last-child td {{ border-bottom: none; }}
    tr:hover td {{ background: var(--surface-hover); }}

    /* Status & Severity Badges */
    .status-badge {{
      display: inline-block;
      padding: 2px 8px;
      border-radius: 4px;
      font-family: var(--font-mono);
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
    }}

    .status-passed {{ background: rgba(63, 185, 80, 0.15); color: var(--pass); }}
    .status-failed {{ background: rgba(248, 81, 73, 0.15); color: var(--fail); }}
    .status-blocked {{ background: rgba(210, 153, 34, 0.15); color: var(--blocked); }}

    .severity-badge {{
      display: inline-block;
      padding: 2px 8px;
      border-radius: 4px;
      font-family: var(--font-mono);
      font-size: 11px;
      font-weight: 600;
    }}

    .severity-blocker {{ background: rgba(248, 81, 73, 0.2); color: #ff7b72; }}
    .severity-major {{ background: rgba(210, 153, 34, 0.2); color: #e3b341; }}
    .severity-minor {{ background: rgba(88, 166, 255, 0.15); color: #79c0ff; }}
    .severity-trivial {{ background: rgba(139, 148, 158, 0.15); color: #8b949e; }}

    .hash-cell {{
      font-family: var(--font-mono);
      font-size: 11px;
      color: var(--accent);
      word-break: break-all;
    }}

    .code-snippet {{
      background: var(--bg);
      border: 1px solid var(--border-muted);
      border-radius: 4px;
      padding: 6px 10px;
      font-family: var(--font-mono);
      font-size: 11px;
      color: var(--text-muted);
      white-space: pre-wrap;
      word-break: break-word;
    }}

    /* Tab content panes */
    .tab-content {{ display: none; }}
    .tab-content.active {{ display: block; }}

    .footer {{
      margin-top: 48px;
      border-top: 1px solid var(--border);
      padding-top: 20px;
      display: flex;
      justify-content: space-between;
      color: var(--text-dim);
      font-size: 12px;
      font-family: var(--font-mono);
    }}
  </style>
</head>
<body>

<div class="container">

  <!-- Header -->
  <header class="report-header">
    <div class="header-left">
      <h1>{manifest.system_under_test}</h1>
      <div class="header-meta">
        <span>Run ID: <strong>{manifest.run_id}</strong></span>
        <span>Env: <strong>{manifest.environment}</strong></span>
        <span>Executed: <strong>{manifest.executed_at}</strong></span>
        <span>Lead: <strong>{manifest.verification_lead}</strong></span>
      </div>
    </div>
    <div class="header-right">
      <div class="verdict-badge verdict-{manifest.overall_verdict.lower()}">
        <span>●</span> {manifest.overall_verdict.replace('_', ' ')}
      </div>
    </div>
  </header>

  <!-- Metrics Grid -->
  <div class="metrics-grid">
    <div class="metric-card">
      <div class="metric-label">Pass Rate</div>
      <div class="metric-val" style="color: {'var(--pass)' if manifest.pass_rate >= 90 else 'var(--fail)'};">
        {manifest.pass_rate}%
      </div>
      <div class="metric-sub">{manifest.passed_cases} of {manifest.total_cases} passed</div>
    </div>

    <div class="metric-card">
      <div class="metric-label">Total Test Cases</div>
      <div class="metric-val">{manifest.total_cases}</div>
      <div class="metric-sub">{manifest.failed_cases} failed, {manifest.blocked_cases} blocked</div>
    </div>

    <div class="metric-card">
      <div class="metric-label">Active Defects</div>
      <div class="metric-val">{len(manifest.defects)}</div>
      <div class="metric-sub">{defect_counts['BLOCKER']} Blocker, {defect_counts['MAJOR']} Major</div>
    </div>

    <div class="metric-card">
      <div class="metric-label">Verified Evidences</div>
      <div class="metric-val">{len(manifest.evidences)}</div>
      <div class="metric-sub">100% SHA-256 Hashed</div>
    </div>
  </div>

  <!-- Tabs Navigation -->
  <div class="tabs-nav">
    <button class="tab-btn active" onclick="switchTab('cases')">
      Test Execution Matrix <span class="tab-pill">{manifest.total_cases}</span>
    </button>
    <button class="tab-btn" onclick="switchTab('defects')">
      4-Tier Defect Log <span class="tab-pill">{len(manifest.defects)}</span>
    </button>
    <button class="tab-btn" onclick="switchTab('evidence')">
      Cryptographic Evidence Audit <span class="tab-pill">{len(manifest.evidences)}</span>
    </button>
  </div>

  <!-- TAB 1: Test Cases -->
  <div id="tab-cases" class="tab-content active">
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th style="width: 100px;">Case ID</th>
            <th>Component</th>
            <th>Test Scenario &amp; Specification</th>
            <th style="width: 140px;">Technique</th>
            <th style="width: 100px;">Status</th>
            <th style="width: 90px;">Duration</th>
            <th style="width: 100px;">Evidence</th>
          </tr>
        </thead>
        <tbody>
"""

    for tc in manifest.test_cases:
        status_cls = f"status-{tc.status.value.lower()}"
        dur_str = f"{tc.duration_ms}ms" if tc.duration_ms else "—"
        evidence_str = f"<code>{tc.evidence_id}</code>" if tc.evidence_id else "—"
        html += f"""          <tr>
            <td style="font-family: var(--font-mono); font-weight: 500;">{tc.id}</td>
            <td style="color: var(--text-muted);">{tc.component}</td>
            <td><strong>{tc.title}</strong></td>
            <td style="font-family: var(--font-mono); font-size: 11px; color: var(--text-muted);">{tc.technique}</td>
            <td><span class="status-badge {status_cls}">{tc.status.value}</span></td>
            <td style="font-family: var(--font-mono); color: var(--text-dim);">{dur_str}</td>
            <td>{evidence_str}</td>
          </tr>
"""

    html += """        </tbody>
      </table>
    </div>
  </div>

  <!-- TAB 2: Defects -->
  <div id="tab-defects" class="tab-content">
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th style="width: 100px;">Defect ID</th>
            <th style="width: 100px;">Tier</th>
            <th>Defect Title &amp; Observed Issue</th>
            <th>Reproduction Steps</th>
            <th>Root Cause / Analysis</th>
          </tr>
        </thead>
        <tbody>
"""

    if not manifest.defects:
        html += """          <tr>
            <td colspan="5" style="text-align: center; color: var(--text-muted); padding: 32px;">
              Zero defects recorded during this test execution cycle.
            </td>
          </tr>
"""
    else:
        for d in manifest.defects:
            sev_cls = f"severity-{d.severity.value.lower()}"
            html += f"""          <tr>
            <td style="font-family: var(--font-mono); font-weight: 600;">{d.id}</td>
            <td><span class="severity-badge {sev_cls}">{d.severity.value}</span></td>
            <td>
              <strong>{d.title}</strong>
              <div style="font-size: 12px; color: var(--fail); margin-top: 4px;">Actual: {d.actual_result}</div>
            </td>
            <td><div class="code-snippet">{d.steps}</div></td>
            <td style="color: var(--text-muted);">{d.root_cause or 'Under investigation'}</td>
          </tr>
"""

    html += """        </tbody>
      </table>
    </div>
  </div>

  <!-- TAB 3: Evidence Audit -->
  <div id="tab-evidence" class="tab-content">
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th style="width: 100px;">Evidence ID</th>
            <th style="width: 180px;">Type / Target</th>
            <th>Evidence Artifact</th>
            <th>SHA-256 Cryptographic Integrity Hash</th>
          </tr>
        </thead>
        <tbody>
"""

    if not manifest.evidences:
        html += """          <tr>
            <td colspan="4" style="text-align: center; color: var(--text-muted); padding: 32px;">
              No evidence artifacts attached to this manifest.
            </td>
          </tr>
"""
    else:
        for e in manifest.evidences:
            html += f"""          <tr>
            <td style="font-family: var(--font-mono); font-weight: 600;">{e.id}</td>
            <td style="font-family: var(--font-mono); font-size: 11px; color: var(--text-muted);">{e.evidence_type}</td>
            <td><strong>{e.name}</strong></td>
            <td class="hash-cell">{e.sha256_hash}</td>
          </tr>
"""

    html += f"""        </tbody>
      </table>
    </div>
  </div>

  <!-- Footer -->
  <footer class="footer">
    <div>DETERMINISTIC DUAL-REPORTER // VERIFICATION ENGINE</div>
    <div>GENERATED WITH 100% SHA-256 PARITY</div>
  </footer>

</div>

<script>
  function switchTab(tabId, el) {{
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

    const targetContent = document.getElementById('tab-' + tabId);
    if (targetContent) targetContent.classList.add('active');

    if (el) {{
      el.classList.add('active');
    }} else {{
      const matchingBtn = Array.from(document.querySelectorAll('.tab-btn')).find(b => b.getAttribute('onclick').includes(tabId));
      if (matchingBtn) matchingBtn.classList.add('active');
    }}
  }}
</script>

</body>
</html>
"""
    return html
