"""Reader transport regressions; fake HTTP only, no model or database requests."""

import unittest
from unittest.mock import Mock, patch

import reader


class ReaderTests(unittest.TestCase):
    def environment(self, key, default=None):
        return {"READER_BASE_URL": "http://127.0.0.1:11434/v1",
                "READER_MODEL": "fixture-model"}.get(key, default)

    def test_length_stop_is_rejected_even_if_content_contains_valid_json(self):
        response = Mock()
        response.json.return_value = {"choices": [{"finish_reason": "length",
                                                   "message": {"content": '{"ok": true}'}}]}
        with patch.object(reader, "env", self.environment), \
             patch.object(reader.requests, "post", return_value=response), \
             patch.object(reader.time, "sleep"), \
             self.assertRaisesRegex(RuntimeError, "reader output truncated"):
            reader.ask("JSON", "test", retries=1)

    def test_explicit_no_reasoning_affects_only_that_request(self):
        response = Mock()
        response.json.return_value = {"choices": [{"finish_reason": "stop",
                                                   "message": {"content": '{"ok": true}'}}]}
        with patch.object(reader, "env", self.environment), \
             patch.object(reader.requests, "post", return_value=response) as post:
            self.assertEqual(reader.ask("JSON", "test", no_reasoning=True), {"ok": True})
            self.assertEqual(post.call_args.kwargs["json"]["reasoning_effort"], "none")
            reader.ask("JSON", "test")
            self.assertNotIn("reasoning_effort", post.call_args.kwargs["json"])
