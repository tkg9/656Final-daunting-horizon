import json
import urllib.error
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from productions.breakdown import OPENROUTER_URL, draft_breakdown
from productions.models import Production, Scene


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return json.dumps(self.payload).encode()


def llm_payload(content):
    return {"choices": [{"message": {"content": content}}]}


class BreakdownTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user("dir@example.com", password="pw-dir-123")
        self.production = Production.objects.create(title="Our Town", created_by=user)
        Scene.objects.create(
            production=self.production,
            number=1,
            heading="SCENE 1. A room.",
            text="SCENE 1. A room.\nANNA: Hi.",
        )

    @override_settings(OPENROUTER_API_KEY="")
    def test_without_a_key_the_parser_is_used_and_nothing_is_called(self):
        with patch("productions.breakdown.urllib.request.urlopen") as urlopen:
            result = draft_breakdown(self.production)
        urlopen.assert_not_called()
        self.assertEqual(result["source"], "rules")
        self.assertEqual(result["characters"], ["ANNA"])

    @override_settings(OPENROUTER_API_KEY="test-key", OPENROUTER_MODEL="test-model")
    @patch("productions.breakdown.urllib.request.urlopen")
    def test_model_json_becomes_the_draft(self, urlopen):
        urlopen.return_value = FakeResponse(llm_payload(json.dumps({
            "characters": ["ANNA"],
            "scenes": [{"number": 1, "characters": ["ANNA"]}],
        })))
        result = draft_breakdown(self.production)
        self.assertEqual(result["source"], "llm")
        self.assertEqual(result["scenes"][0]["heading"], "SCENE 1. A room.")
        self.assertEqual(result["scenes"][0]["characters"], ["ANNA"])
        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, OPENROUTER_URL)
        self.assertEqual(request.get_header("Authorization"), "Bearer test-key")
        body = json.loads(request.data.decode())
        self.assertEqual(body["model"], "test-model")
        self.assertNotIn("test-key", body["messages"][1]["content"])

    @override_settings(OPENROUTER_API_KEY="test-key")
    @patch("productions.breakdown.urllib.request.urlopen")
    def test_fenced_json_is_accepted(self, urlopen):
        fenced = '```json\n{"characters": ["ANNA"], "scenes": [{"number": 1, "characters": ["ANNA"]}]}\n```'
        urlopen.return_value = FakeResponse(llm_payload(fenced))
        self.assertEqual(draft_breakdown(self.production)["source"], "llm")

    @override_settings(OPENROUTER_API_KEY="test-key")
    @patch("productions.breakdown.urllib.request.urlopen", side_effect=urllib.error.URLError("down"))
    def test_a_failed_call_falls_back_to_the_parser(self, urlopen):
        result = draft_breakdown(self.production)
        self.assertEqual(result["source"], "rules")
        self.assertEqual(result["characters"], ["ANNA"])
        urlopen.assert_called_once()
