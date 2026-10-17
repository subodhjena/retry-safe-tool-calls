from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import tempfile
import unittest

from operations import IntentConflict, counts, create_task, initialize


class OperationTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = Path(self.folder.name) / "tasks.sqlite"
        initialize(self.path)

    def call(self, **kwargs):
        return create_task(self.path, "acme", "op-1", "Check delivery", **kwargs)

    def test_response_lost_after_commit(self):
        with self.assertRaises(TimeoutError):
            self.call(fail_at="after_commit")
        self.assertEqual(counts(self.path), (1, 1))
        self.assertEqual(self.call(), {"task_id": 1, "status": "created"})
        self.assertEqual(counts(self.path), (1, 1))

    def test_both_records_rollback_before_commit(self):
        with self.assertRaises(ConnectionError):
            self.call(fail_at="before_commit")
        self.assertEqual(counts(self.path), (0, 0))
        self.call()
        self.assertEqual(counts(self.path), (1, 1))

    def test_concurrent_delivery_of_same_intent(self):
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda _: self.call(), range(16)))
        self.assertTrue(all(result == results[0] for result in results))
        self.assertEqual(counts(self.path), (1, 1))

    def test_conflicting_arguments_do_not_mutate(self):
        self.call()
        with self.assertRaises(IntentConflict):
            create_task(self.path, "acme", "op-1", "Different subject")
        self.assertEqual(counts(self.path), (1, 1))

    def test_new_intent_same_subject_creates_new_task(self):
        first = self.call()
        second = create_task(self.path, "acme", "op-2", "Check delivery")
        self.assertNotEqual(first["task_id"], second["task_id"])
        self.assertEqual(counts(self.path), (2, 2))

    def test_tenant_scope(self):
        self.call()
        create_task(self.path, "other", "op-1", "Check delivery")
        self.assertEqual(counts(self.path), (2, 2))

    def test_invalid_request_does_not_mutate(self):
        with self.assertRaises(ValueError):
            create_task(self.path, "acme", "", "Check delivery")
        self.assertEqual(counts(self.path), (0, 0))


if __name__ == "__main__":
    unittest.main()
