from __future__ import annotations

import unittest
from lab_repo_kit.init_repo import (
    ALLOWED_CATEGORIES,
    build_topic_list,
    init_repository,
    resolve_template,
)


class TestInitRepo(unittest.TestCase):
    def test_resolve_template_aliases(self) -> None:
        self.assertEqual(resolve_template("vr"), "Tran-Memory-Lab/template-vr-experiment")
        self.assertEqual(resolve_template("data"), "Tran-Memory-Lab/template-data-pipeline")
        self.assertEqual(resolve_template(None), None)
        self.assertEqual(resolve_template("my-custom-template"), "Tran-Memory-Lab/my-custom-template")
        self.assertEqual(resolve_template("OtherOrg/tmpl"), "OtherOrg/tmpl")

    def test_build_topic_list(self) -> None:
        # task-desktop gets 'desktop-task' as baseline
        topics = build_topic_list("task-desktop", ["psychopy", "attention"])
        self.assertEqual(topics, ["desktop-task", "psychopy", "attention"])

        # Deduplication preserving order
        topics_dedup = build_topic_list("experiment-vr", ["vr-experiment", "eye-tracking", "VR-EXPERIMENT"])
        self.assertEqual(topics_dedup, ["vr-experiment", "eye-tracking"])

    def test_init_repository_invalid_category(self) -> None:
        ret = init_repository("test-repo", category="non-existent-category")
        self.assertEqual(ret, 1)

    def test_init_repository_dry_run(self) -> None:
        ret = init_repository(
            name="test-repo",
            category="task-desktop",
            template="data",
            extra_topics=["memory"],
            dry_run=True,
        )
        self.assertEqual(ret, 0)


if __name__ == "__main__":
    unittest.main()
