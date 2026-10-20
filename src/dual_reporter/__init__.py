"""Deterministic Dual-Reporter package."""

from .models import TestRunManifest, TestCaseItem, DefectItem, EvidenceItem, DefectSeverity, TestStatus
from .html_builder import render_html_report
from .docx_builder import build_docx_report

__version__ = "1.0.0"
__all__ = [
    "TestRunManifest",
    "TestCaseItem",
    "DefectItem",
    "EvidenceItem",
    "DefectSeverity",
    "TestStatus",
    "render_html_report",
    "build_docx_report",
]
