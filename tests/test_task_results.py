import unittest

from execution.task_results import TaskResultTracker, TaskStateError, TaskStatus


class TestTaskResultTracker(unittest.TestCase):
    def setUp(self):
        self.tracker = TaskResultTracker()

    def test_successful_lifecycle(self):
        submitted = self.tracker.submit("task-1")
        self.assertEqual(submitted["status"], TaskStatus.SUBMITTED.value)

        running = self.tracker.mark_running("task-1")
        self.assertEqual(running["status"], TaskStatus.RUNNING.value)
        self.assertIsNotNone(running["started_at"])

        completed = self.tracker.mark_success("task-1", "encoded-result")
        self.assertEqual(completed["status"], TaskStatus.SUCCESS.value)
        self.assertEqual(completed["result_data"], "encoded-result")
        self.assertIsNotNone(completed["completed_at"])

    def test_failed_lifecycle(self):
        self.tracker.submit("task-2")
        self.tracker.mark_running("task-2")
        failed = self.tracker.mark_failed("task-2", "ValueError", "invalid input")
        self.assertEqual(failed["status"], TaskStatus.FAILED.value)
        self.assertEqual(failed["error_type"], "ValueError")
        self.assertEqual(failed["error_message"], "invalid input")

    def test_failure_can_be_recorded_before_execution_starts(self):
        self.tracker.submit("task-3")
        failed = self.tracker.mark_failed("task-3", "TaskPayloadError", "bad payload")
        self.assertEqual(failed["status"], TaskStatus.FAILED.value)

    def test_invalid_state_transition_is_rejected(self):
        self.tracker.submit("task-4")
        with self.assertRaises(TaskStateError):
            self.tracker.mark_success("task-4", "result")

    def test_terminal_task_cannot_be_changed(self):
        self.tracker.submit("task-5")
        self.tracker.mark_running("task-5")
        self.tracker.mark_success("task-5", "result")
        with self.assertRaises(TaskStateError):
            self.tracker.mark_failed("task-5", "RuntimeError", "late failure")

    def test_duplicate_task_id_is_rejected(self):
        self.tracker.submit("task-6")
        with self.assertRaises(TaskStateError):
            self.tracker.submit("task-6")

    def test_oldest_completed_record_is_evicted_at_capacity(self):
        tracker = TaskResultTracker(max_records=2)
        tracker.submit("first")
        tracker.mark_running("first")
        tracker.mark_success("first", "one")
        tracker.submit("second")
        tracker.mark_running("second")
        tracker.mark_success("second", "two")
        tracker.submit("third")

        with self.assertRaises(TaskStateError):
            tracker.get("first")
        self.assertEqual(tracker.get("second")["status"], "SUCCESS")
        self.assertEqual(tracker.get("third")["status"], "SUBMITTED")

    def test_active_tasks_are_not_evicted(self):
        tracker = TaskResultTracker(max_records=1)
        tracker.submit("active")
        with self.assertRaises(TaskStateError):
            tracker.submit("next")
        self.assertEqual(tracker.get("active")["status"], "SUBMITTED")

    def test_input_validation(self):
        with self.assertRaises(ValueError):
            TaskResultTracker(max_records=0)
        with self.assertRaises(ValueError):
            self.tracker.submit("")


if __name__ == "__main__":
    unittest.main()
