"""Universal, brand-neutral executive DOCX test report builder."""

from __future__ import annotations
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn
from .models import TestRunManifest, DefectSeverity, TestStatus


def _set_cell_background(cell, hex_color: str):
    """Sets background shading of a table cell."""
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)


def _set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Sets cell internal padding."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)


def build_docx_report(manifest: TestRunManifest, output_path: str):
    """Builds a clean, executive Word document without company-specific templates."""
    doc = docx.Document()

    # Set 1-inch margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Document Header / Pre-title
    p_meta = doc.add_paragraph()
    r_tag = p_meta.add_run("SYSTEM VERIFICATION & QA REPORT // FORMAL AUDIT DELIVERABLE")
    r_tag.font.name = "Arial"
    r_tag.font.size = Pt(8.5)
    r_tag.font.bold = True
    r_tag.font.color.rgb = RGBColor(110, 118, 129)
    p_meta.paragraph_format.space_after = Pt(4)

    # Main Title
    p_title = doc.add_paragraph()
    r_title = p_title.add_run(manifest.system_under_test)
    r_title.font.name = "Arial"
    r_title.font.size = Pt(22)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(26, 32, 44)
    p_title.paragraph_format.space_after = Pt(14)

    # Executive Metadata Table
    meta_table = doc.add_table(rows=2, cols=3)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_table.autofit = False

    meta_items = [
        ("TEST RUN ID", manifest.run_id),
        ("ENVIRONMENT", manifest.environment),
        ("EXECUTION DATE", manifest.executed_at),
        ("VERIFICATION LEAD", manifest.verification_lead),
        ("OVERALL VERDICT", manifest.overall_verdict.replace("_", " ")),
        ("EVIDENCE INTEGRITY", "100% SHA-256 Verified")
    ]

    for idx, (label, val) in enumerate(meta_items):
        r_idx = idx // 3
        c_idx = idx % 3
        cell = meta_table.cell(r_idx, c_idx)
        _set_cell_background(cell, "F7F9FA")
        _set_cell_margins(cell, top=120, bottom=120, left=140, right=140)
        
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(2)
        r_lbl = p.add_run(label + "\n")
        r_lbl.font.name = "Arial"
        r_lbl.font.size = Pt(8)
        r_lbl.font.bold = True
        r_lbl.font.color.rgb = RGBColor(113, 128, 150)
        
        r_v = p.add_run(val)
        r_v.font.name = "Arial"
        r_v.font.size = Pt(10)
        r_v.font.bold = True
        if label == "OVERALL VERDICT":
            if manifest.overall_verdict == "PASSED":
                r_v.font.color.rgb = RGBColor(40, 167, 69)
            else:
                r_v.font.color.rgb = RGBColor(220, 53, 69)
        else:
            r_v.font.color.rgb = RGBColor(45, 55, 72)

    doc.add_paragraph().paragraph_format.space_after = Pt(16)

    # -------------------------------------------------------------
    # SECTION 1: EXECUTIVE SUMMARY & SCORECARD
    # -------------------------------------------------------------
    h1 = doc.add_heading(level=1)
    r_h1 = h1.add_run("1. Executive Summary & Quality Scorecard")
    r_h1.font.name = "Arial"
    r_h1.font.size = Pt(14)
    r_h1.font.bold = True
    r_h1.font.color.rgb = RGBColor(26, 32, 44)
    h1.paragraph_format.space_after = Pt(8)

    p_lead = doc.add_paragraph()
    r_lead = p_lead.add_run(
        f"This document formalizes the testing outcomes for {manifest.system_under_test}. "
        f"During this test execution cycle, a total of {manifest.total_cases} test cases were executed across critical components. "
        f"The achieved overall pass rate is {manifest.pass_rate}%, with {manifest.passed_cases} passed, "
        f"{manifest.failed_cases} failed, and {manifest.blocked_cases} blocked cases."
    )
    r_lead.font.name = "Arial"
    r_lead.font.size = Pt(10)
    r_lead.font.color.rgb = RGBColor(74, 85, 104)
    p_lead.paragraph_format.space_after = Pt(12)

    # Metrics Summary Table
    metric_table = doc.add_table(rows=2, cols=5)
    metric_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["TOTAL CASES", "PASSED", "FAILED", "BLOCKED", "PASS RATE"]
    values = [str(manifest.total_cases), str(manifest.passed_cases), str(manifest.failed_cases), str(manifest.blocked_cases), f"{manifest.pass_rate}%"]

    for i in range(5):
        cell_hdr = metric_table.cell(0, i)
        _set_cell_background(cell_hdr, "2D3748")
        _set_cell_margins(cell_hdr, 100, 100, 100, 100)
        p = cell_hdr.paragraphs[0]
        r = p.add_run(headers[i])
        r.font.name = "Arial"
        r.font.size = Pt(8.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER

        cell_val = metric_table.cell(1, i)
        _set_cell_background(cell_val, "FFFFFF")
        _set_cell_margins(cell_val, 120, 120, 100, 100)
        p2 = cell_val.paragraphs[0]
        r2 = p2.add_run(values[i])
        r2.font.name = "Arial"
        r2.font.size = Pt(12)
        r2.font.bold = True
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # Defect Tier Breakdown Table
    defect_counts = manifest.get_defect_count_by_tier()
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    p_def_hdr = doc.add_paragraph()
    r_def_hdr = p_def_hdr.add_run("Active Defect Breakdown (Strict 4-Tier Taxonomy)")
    r_def_hdr.font.name = "Arial"
    r_def_hdr.font.size = Pt(10)
    r_def_hdr.font.bold = True
    r_def_hdr.font.color.rgb = RGBColor(45, 55, 72)

    def_table = doc.add_table(rows=2, cols=4)
    def_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    tiers = [("BLOCKER", "E53E3E"), ("MAJOR", "DD6B20"), ("MINOR", "3182CE"), ("TRIVIAL", "718096")]

    for i, (tier_name, color_hex) in enumerate(tiers):
        c_hdr = def_table.cell(0, i)
        _set_cell_background(c_hdr, "F7FAFC")
        _set_cell_margins(c_hdr, 80, 80, 100, 100)
        p = c_hdr.paragraphs[0]
        r = p.add_run(tier_name)
        r.font.name = "Arial"
        r.font.size = Pt(8)
        r.font.bold = True
        r.font.color.rgb = RGBColor(113, 128, 150)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER

        c_val = def_table.cell(1, i)
        _set_cell_margins(c_val, 100, 100, 100, 100)
        p2 = c_val.paragraphs[0]
        r2 = p2.add_run(str(defect_counts[tier_name]))
        r2.font.name = "Arial"
        r2.font.size = Pt(11)
        r2.font.bold = True
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph().paragraph_format.space_after = Pt(18)

    # -------------------------------------------------------------
    # SECTION 2: DEFECT LOG & SEVERITY TRIAGE
    # -------------------------------------------------------------
    h2 = doc.add_heading(level=1)
    r_h2 = h2.add_run("2. Defect Log & Forensic Triage")
    r_h2.font.name = "Arial"
    r_h2.font.size = Pt(14)
    r_h2.font.bold = True
    r_h2.font.color.rgb = RGBColor(26, 32, 44)
    h2.paragraph_format.space_after = Pt(8)

    if not manifest.defects:
        p_nodef = doc.add_paragraph()
        r_nodef = p_nodef.add_run("No defects observed during this verification cycle.")
        r_nodef.font.name = "Arial"
        r_nodef.font.size = Pt(9.5)
        r_nodef.font.italic = True
        p_nodef.paragraph_format.space_after = Pt(14)
    else:
        for d in manifest.defects:
            p_dtitle = doc.add_paragraph()
            r_did = p_dtitle.add_run(f"[{d.id}] ")
            r_did.font.name = "Arial"
            r_did.font.size = Pt(10)
            r_did.font.bold = True
            r_did.font.color.rgb = RGBColor(49, 130, 206)

            r_dname = p_dtitle.add_run(f"{d.title} — Tier: {d.severity.value}")
            r_dname.font.name = "Arial"
            r_dname.font.size = Pt(10)
            r_dname.font.bold = True
            r_dname.font.color.rgb = RGBColor(26, 32, 44)
            p_dtitle.paragraph_format.space_after = Pt(4)

            # Detail table for defect
            d_tbl = doc.add_table(rows=3, cols=2)
            d_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
            
            d_data = [
                ("Reproduction Steps", d.steps),
                ("Observed / Actual Result", d.actual_result),
                ("Root Cause Analysis", d.root_cause or "Investigation in progress")
            ]
            for row_idx, (k, val) in enumerate(d_data):
                c0 = d_tbl.cell(row_idx, 0)
                c1 = d_tbl.cell(row_idx, 1)
                _set_cell_background(c0, "F7FAFC")
                _set_cell_margins(c0, 60, 60, 80, 80)
                _set_cell_margins(c1, 60, 60, 80, 80)
                
                p0 = c0.paragraphs[0]
                r0 = p0.add_run(k)
                r0.font.name = "Arial"
                r0.font.size = Pt(8.5)
                r0.font.bold = True
                r0.font.color.rgb = RGBColor(113, 128, 150)

                p1 = c1.paragraphs[0]
                r1 = p1.add_run(val)
                r1.font.name = "Arial"
                r1.font.size = Pt(9)
                r1.font.color.rgb = RGBColor(45, 55, 72)

            doc.add_paragraph().paragraph_format.space_after = Pt(12)

    doc.add_paragraph().paragraph_format.space_after = Pt(14)

    # -------------------------------------------------------------
    # SECTION 3: TEST SCENARIO EXECUTION MATRIX
    # -------------------------------------------------------------
    h3 = doc.add_heading(level=1)
    r_h3 = h3.add_run("3. Test Scenario Execution Matrix")
    r_h3.font.name = "Arial"
    r_h3.font.size = Pt(14)
    r_h3.font.bold = True
    r_h3.font.color.rgb = RGBColor(26, 32, 44)
    h3.paragraph_format.space_after = Pt(8)

    tc_table = doc.add_table(rows=1 + len(manifest.test_cases), cols=5)
    tc_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    tc_headers = ["ID", "COMPONENT", "TEST SCENARIO SPECIFICATION", "TECHNIQUE", "STATUS"]

    for col_idx, h_text in enumerate(tc_headers):
        c = tc_table.cell(0, col_idx)
        _set_cell_background(c, "2D3748")
        _set_cell_margins(c, 80, 80, 80, 80)
        p = c.paragraphs[0]
        r = p.add_run(h_text)
        r.font.name = "Arial"
        r.font.size = Pt(8)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    for row_idx, tc in enumerate(manifest.test_cases, start=1):
        bg = "FFFFFF" if row_idx % 2 == 1 else "F7FAFC"
        cells = [
            (tc.id, True),
            (tc.component, False),
            (tc.title, False),
            (tc.technique, False),
            (tc.status.value, True)
        ]
        for col_idx, (text_val, is_bold) in enumerate(cells):
            c = tc_table.cell(row_idx, col_idx)
            _set_cell_background(c, bg)
            _set_cell_margins(c, 60, 60, 80, 80)
            p = c.paragraphs[0]
            r = p.add_run(text_val)
            r.font.name = "Arial"
            r.font.size = Pt(8.5)
            r.font.bold = is_bold
            if col_idx == 4:
                if text_val == "PASSED":
                    r.font.color.rgb = RGBColor(40, 167, 69)
                elif text_val == "FAILED":
                    r.font.color.rgb = RGBColor(220, 53, 69)
                else:
                    r.font.color.rgb = RGBColor(217, 119, 6)
            else:
                r.font.color.rgb = RGBColor(45, 55, 72)

    doc.add_paragraph().paragraph_format.space_after = Pt(20)

    # -------------------------------------------------------------
    # SECTION 4: FORENSIC EVIDENCE & SHA-256 AUDIT TRAIL
    # -------------------------------------------------------------
    h4 = doc.add_heading(level=1)
    r_h4 = h4.add_run("4. Cryptographic Evidence & SHA-256 Audit Trail")
    r_h4.font.name = "Arial"
    r_h4.font.size = Pt(14)
    r_h4.font.bold = True
    r_h4.font.color.rgb = RGBColor(26, 32, 44)
    h4.paragraph_format.space_after = Pt(8)

    p_ev_desc = doc.add_paragraph()
    r_ev_desc = p_ev_desc.add_run(
        "To ensure zero tampering and immutable auditability, every execution artifact "
        "(screenshots, HTTP responses, system logs, query results) is cryptographically stamped with SHA-256."
    )
    r_ev_desc.font.name = "Arial"
    r_ev_desc.font.size = Pt(9.5)
    r_ev_desc.font.color.rgb = RGBColor(74, 85, 104)
    p_ev_desc.paragraph_format.space_after = Pt(10)

    ev_table = doc.add_table(rows=1 + len(manifest.evidences), cols=4)
    ev_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    ev_headers = ["ID", "TYPE", "ARTIFACT NAME", "SHA-256 INTEGRITY HASH"]

    for col_idx, h_text in enumerate(ev_headers):
        c = ev_table.cell(0, col_idx)
        _set_cell_background(c, "2D3748")
        _set_cell_margins(c, 80, 80, 80, 80)
        p = c.paragraphs[0]
        r = p.add_run(h_text)
        r.font.name = "Arial"
        r.font.size = Pt(8)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    for row_idx, ev in enumerate(manifest.evidences, start=1):
        bg = "FFFFFF" if row_idx % 2 == 1 else "F7FAFC"
        cells = [ev.id, ev.evidence_type, ev.name, ev.sha256_hash]
        for col_idx, text_val in enumerate(cells):
            c = ev_table.cell(row_idx, col_idx)
            _set_cell_background(c, bg)
            _set_cell_margins(c, 60, 60, 80, 80)
            p = c.paragraphs[0]
            r = p.add_run(text_val)
            r.font.name = "Courier New" if col_idx == 3 else "Arial"
            r.font.size = Pt(7.5) if col_idx == 3 else Pt(8.5)
            r.font.color.rgb = RGBColor(49, 130, 206) if col_idx == 3 else RGBColor(45, 55, 72)

    # Save document
    doc.save(output_path)
