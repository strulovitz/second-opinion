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

    def test_json_constraint_is_opt_in_and_text_cannot_request_it(self):
        response = Mock()
        response.json.return_value = {"choices": [{"finish_reason": "stop",
                                                   "message": {"content": '{"ok": true}'}}]}
        with patch.object(reader, "env", self.environment), \
             patch.object(reader.requests, "post", return_value=response) as post:
            self.assertEqual(reader.ask("JSON", "test", json_output=True), {"ok": True})
            self.assertEqual(post.call_args.kwargs["json"]["response_format"], {"type": "json_object"})
            reader.ask("JSON", "test")
            self.assertNotIn("response_format", post.call_args.kwargs["json"])
            with self.assertRaisesRegex(ValueError, "requires expect_json"):
                reader.ask("Text", "test", json_output=True, expect_json=False)

    def test_full_schema_is_request_local_and_requires_json(self):
        response = Mock()
        response.json.return_value = {"choices": [{"finish_reason": "stop",
                                                   "message": {"content": '{"ok": true}'}}]}
        schema = {"type": "object", "properties": {"ok": {"type": "boolean"}}}
        with patch.object(reader, "env", self.environment), \
             patch.object(reader.requests, "post", return_value=response) as post:
            reader.ask("JSON", "test", response_schema=schema,
                       temperature=0.7, top_p=0.8, presence_penalty=1.5)
            self.assertEqual(post.call_args.kwargs["json"]["response_format"], {
                "type": "json_schema", "json_schema": {
                    "name": "reader_response", "strict": True, "schema": schema}})
            self.assertEqual(post.call_args.kwargs["json"]["temperature"], 0.7)
            self.assertEqual(post.call_args.kwargs["json"]["top_p"], 0.8)
            self.assertEqual(post.call_args.kwargs["json"]["presence_penalty"], 1.5)
            reader.ask("JSON", "test")
            self.assertNotIn("response_format", post.call_args.kwargs["json"])
            self.assertNotIn("top_p", post.call_args.kwargs["json"])
            self.assertNotIn("presence_penalty", post.call_args.kwargs["json"])
            with self.assertRaisesRegex(ValueError, "requires expect_json"):
                reader.ask("Text", "test", response_schema=schema, expect_json=False)

    def test_raw_completion_is_captured_before_json_or_length_rejection(self):
        for content, finish in [('{"entries":[{"headword":"Alpha"}', "stop"),
                                ('{"ok": true}', "length")]:
            response = Mock()
            completion = {"choices": [{"finish_reason": finish, "message": {"content": content}}]}
            response.json.return_value = completion
            capture = Mock()
            with patch.object(reader, "env", self.environment), \
                 patch.object(reader.requests, "post", return_value=response), \
                 patch.object(reader.time, "sleep"), self.assertRaises(RuntimeError):
                reader.ask("JSON", "test", retries=1, on_response=capture)
            evidence = capture.call_args.args[0]
            self.assertEqual(evidence["response"], completion)
            self.assertEqual(set(evidence), {"request", "response"})
            self.assertNotIn("READER_BASE_URL", str(evidence))
