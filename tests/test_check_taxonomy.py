from __future__ import annotations

import unittest
from lab_repo_kit.check_taxonomy import audit_repository


class TestCheckTaxonomy(unittest.TestCase):
    def test_audit_repository_success(self) -> None:
        compliant, issues = audit_repository("open-attention-battery", "task-desktop", ["desktop-task", "psychopy"])
        self.assertTrue(compliant)
        self.assertEqual(len(issues), 0)

    def test_audit_repository_missing_category(self) -> None:
        compliant, issues = audit_repository("unassigned-repo", None, ["desktop-task"])
        self.assertFalse(compliant)
        self.assertTrue(any("Missing 'repo-category'" in issue for issue in issues))

    def test_audit_repository_invalid_category(self) -> None:
        compliant, issues = audit_repository("bad-repo", "invalid-category", ["desktop-task"])
        self.assertFalse(compliant)
        self.assertTrue(any("Invalid 'repo-category'" in issue for issue in issues))

    def test_audit_repository_missing_topics(self) -> None:
        compliant, issues = audit_repository("empty-topics", "task-desktop", [])
        self.assertFalse(compliant)
        self.assertTrue(any("No repository topics assigned" in issue for issue in issues))

    def test_audit_repository_missing_baseline_topic(self) -> None:
        # Category is task-desktop, but topic is only 'python' without 'desktop-task'
        compliant, issues = audit_repository("mismatch-repo", "task-desktop", ["python", "spatial-memory"])
        self.assertFalse(compliant)
        self.assertTrue(any("Missing expected baseline topic" in issue for issue in issues))

        # With strict=False, baseline topic check is bypassed
        compliant_relaxed, issues_relaxed = audit_repository(
            "mismatch-repo", "task-desktop", ["python", "spatial-memory"], strict=False
        )
        self.assertTrue(compliant_relaxed)
        self.assertEqual(len(issues_relaxed), 0)


if __name__ == "__main__":
    unittest.main()
