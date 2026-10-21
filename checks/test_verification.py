"""Focused checks for the agent's evidence and malformed-response boundaries."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from langchain_core.messages import AIMessage, ToolMessage
from starter.agent import validate_response, verify


def request(name, call_id):
    return AIMessage(content="", tool_calls=[{
        "name": name, "args": {}, "id": call_id, "type": "tool_call",
    }])


def observation(name, call_id, content, **kwargs):
    return ToolMessage(name=name, tool_call_id=call_id, content=content, **kwargs)


class VerificationBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.passing = [request("run_tests", "test-1"),
                        observation("run_tests", "test-1", "exit_code=0\nOK")]
        self.final = AIMessage(content="Observed test results.")

    def status(self, messages):
        result = verify({"messages": messages})
        self.assertTrue(result["reason"])
        return result["completion_status"]

    def test_response_validation_rejects_non_message(self):
        with self.assertRaises(ValueError):
            validate_response({"content": "done"})

    def test_response_validation_rejects_malformed_native_call(self):
        message = AIMessage(content="", invalid_tool_calls=[{
            "name": "run_tests", "args": "{", "id": "bad", "error": "Invalid JSON",
        }])
        with self.assertRaises(ValueError):
            validate_response(message)

    def test_json_looking_text_remains_text(self):
        message = AIMessage(content='{"name": "run_tests", "args": {}}')
        self.assertIs(validate_response(message), message)
        self.assertEqual(message.tool_calls, [])
        self.assertEqual(self.status([message]), "incomplete")

    def test_linked_passing_tests_verify(self):
        self.assertEqual(self.status([*self.passing, self.final]), "verified")

    def test_unlinked_or_misnamed_observations_cannot_verify(self):
        for message in [observation("run_tests", "unknown", "exit_code=0\nOK"),
                        observation("read_file", "test-1", "exit_code=0\nOK")]:
            with self.subTest(message=message):
                self.assertEqual(self.status([self.passing[0], message, self.final]), "incomplete")

    def test_edit_invalidates_passing_tests(self):
        edit = [request("edit_pricing", "edit-1"),
                observation("edit_pricing", "edit-1", "Updated orders/pricing.py once")]
        self.assertEqual(self.status([*self.passing, *edit, self.final]), "incomplete")

    def test_failed_edit_does_not_invalidate_unchanged_code(self):
        edit = [request("edit_pricing", "edit-1"),
                observation("edit_pricing", "edit-1", "ERROR: ambiguous replacement")]
        self.assertEqual(self.status([*self.passing, *edit, self.final]), "verified")

    def test_later_unsuccessful_tests_clear_success(self):
        for content in ["exit_code=1\nFAILED", "DENIED: approval withheld", "ERROR: timeout"]:
            with self.subTest(content=content):
                later = [request("run_tests", "test-2"), observation("run_tests", "test-2", content)]
                self.assertEqual(self.status([*self.passing, *later, self.final]), "incomplete")

    def test_error_status_and_false_exit_code_do_not_pass(self):
        for message in [observation("run_tests", "test-1", "exit_code=0\nOK", status="error"),
                        observation("run_tests", "test-1", "exit_code=01\nFAILED")]:
            with self.subTest(message=message):
                self.assertEqual(self.status([self.passing[0], message, self.final]), "incomplete")

    def test_empty_final_or_pending_call_prevents_verification(self):
        for final in [AIMessage(content="  "), request("read_file", "pending")]:
            with self.subTest(final=final):
                self.assertEqual(self.status([*self.passing, final]), "incomplete")

    def test_passing_retry_after_edit_restores_verification(self):
        edit = [request("edit_pricing", "edit-1"),
                observation("edit_pricing", "edit-1", "Updated orders/pricing.py once")]
        self.assertEqual(self.status([*edit, *self.passing, self.final]), "verified")


if __name__ == "__main__":
    unittest.main()
