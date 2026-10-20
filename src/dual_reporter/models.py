"""Data models for deterministic test execution, defects, and evidence tracking."""

from __future__ import annotations
import hashlib
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any


class DefectSeverity(str, Enum):
    BLOCKER = "BLOCKER"
    MAJOR = "MAJOR"
    MINOR = "MINOR"
    TRIVIAL = "TRIVIAL"


class TestStatus(str, Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"


@dataclass
class EvidenceItem:
    id: str
    name: str
    evidence_type: str  # e.g. "API_PAYLOAD", "SCREENSHOT", "LOG_SNIPPET", "SQL_RECORDSET"
    content_or_path: str
    sha256_hash: str = ""

    def __post_init__(self):
        if not self.sha256_hash and self.content_or_path:
            # Generate deterministic SHA-256
            self.sha256_hash = hashlib.sha256(self.content_or_path.encode("utf-8")).hexdigest()


@dataclass
class DefectItem:
    id: str
    title: str
    severity: DefectSeverity
    steps: str
    expected_result: str
    actual_result: str
    root_cause: str = ""
    evidence_ref: str = ""


@dataclass
class TestCaseItem:
    id: str
    title: str
    component: str
    technique: str  # e.g., "BVA", "EQUIVALENCE_PARTITIONING", "BOUNDARY_ANALYSIS", "HAPPY_PATH"
    status: TestStatus
    duration_ms: int = 0
    defect_id: Optional[str] = None
    evidence_id: Optional[str] = None


@dataclass
class TestRunManifest:
    run_id: str
    system_under_test: str
    environment: str
    executed_at: str
    verification_lead: str
    test_cases: List[TestCaseItem] = field(default_factory=list)
    defects: List[DefectItem] = field(default_factory=list)
    evidences: List[EvidenceItem] = field(default_factory=list)

    @property
    def total_cases(self) -> int:
        return len(self.test_cases)

    @property
    def passed_cases(self) -> int:
        return sum(1 for c in self.test_cases if c.status == TestStatus.PASSED)

    @property
    def failed_cases(self) -> int:
        return sum(1 for c in self.test_cases if c.status == TestStatus.FAILED)

    @property
    def blocked_cases(self) -> int:
        return sum(1 for c in self.test_cases if c.status == TestStatus.BLOCKED)

    @property
    def pass_rate(self) -> float:
        if not self.test_cases:
            return 0.0
        return round((self.passed_cases / len(self.test_cases)) * 100, 1)

    @property
    def overall_verdict(self) -> str:
        if self.failed_cases > 0 or any(d.severity == DefectSeverity.BLOCKER for d in self.defects):
            return "FAILED"
        if self.blocked_cases > 0:
            return "CONDITIONALLY_PASSED"
        return "PASSED"

    def get_defect_count_by_tier(self) -> Dict[str, int]:
        counts = {tier.value: 0 for tier in DefectSeverity}
        for d in self.defects:
            counts[d.severity.value] += 1
        return counts

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TestRunManifest:
        evidences = [
            EvidenceItem(
                id=e["id"],
                name=e["name"],
                evidence_type=e.get("evidence_type", "LOG"),
                content_or_path=e.get("content_or_path", ""),
                sha256_hash=e.get("sha256_hash", "")
            )
            for e in data.get("evidences", [])
        ]
        
        defects = [
            DefectItem(
                id=d["id"],
                title=d["title"],
                severity=DefectSeverity(d.get("severity", "MINOR").upper()),
                steps=d.get("steps", ""),
                expected_result=d.get("expected_result", ""),
                actual_result=d.get("actual_result", ""),
                root_cause=d.get("root_cause", ""),
                evidence_ref=d.get("evidence_ref", "")
            )
            for d in data.get("defects", [])
        ]

        test_cases = [
            TestCaseItem(
                id=tc["id"],
                title=tc["title"],
                component=tc.get("component", "General"),
                technique=tc.get("technique", "FUNCTIONAL"),
                status=TestStatus(tc.get("status", "PASSED").upper()),
                duration_ms=tc.get("duration_ms", 0),
                defect_id=tc.get("defect_id"),
                evidence_id=tc.get("evidence_id")
            )
            for tc in data.get("test_cases", [])
        ]

        return cls(
            run_id=data.get("run_id", "RUN-001"),
            system_under_test=data.get("system_under_test", "Enterprise System"),
            environment=data.get("environment", "STAGING / SIT"),
            executed_at=data.get("executed_at", ""),
            verification_lead=data.get("verification_lead", "Aldyan Saputra"),
            test_cases=test_cases,
            defects=defects,
            evidences=evidences
        )
