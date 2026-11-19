"""Productions and the AI breakdown. No test reaches OpenRouter: the HTTP call
or chat() is mocked, and the test runner blanks the real key."""
import io
import json
import urllib.error
from unittest import mock

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase, override_settings

from productions import llm
from productions.breakdown import MAX_SCRIPT_CHARS, draft_breakdown, parse_breakdown
from productions.llm import LLMError
from productions.models import Breakdown, Production

GOOD_REPLY = json.dumps({
    "characters": [{"name": "MARA", "description": "The lighthouse keeper"}],
    "scenes": [{"title": "The lamp room", "characters": ["MARA", "TOM"]}],
    "props": ["brass scissors", "lantern"],
    "costumes": ["oilskin coat"],
    "set_pieces": ["the great lamp"],
    "cues": [{"scene": "The lamp room", "kind": "Sound", "description": "Thunder"}],
})


def fake_openrouter_response(content, **extra):
    """Something urlopen() can return, as a context manager, with an OpenRouter-shaped body."""
    body = {"choices": [{"message": {"role": "assistant", "content": content}}], **extra}
    response = mock.MagicMock()
    response.__enter__.return_value = io.BytesIO(json.dumps(body).encode())
    return response


class NoRealLLMInTestsTests(SimpleTestCase):
    def test_runner_blanks_the_openrouter_key(self):
        self.assertEqual(settings.OPENROUTER_API_KEY, "")

    @mock.patch("productions.llm.urllib.request.urlopen")
    def test_chat_without_key_never_makes_a_request(self, urlopen):
        with self.assertRaisesMessage(LLMError, "not configured"):
            llm.chat([{"role": "user", "content": "hi"}])
        urlopen.assert_not_called()


@override_settings(OPENROUTER_API_KEY="test-key", OPENROUTER_MODEL="test/model")
class ChatClientTests(SimpleTestCase):
    @mock.patch("productions.llm.urllib.request.urlopen")
    def test_sends_model_messages_and_key_to_openrouter(self, urlopen):
        urlopen.return_value = fake_openrouter_response("hello")
        reply = llm.chat([{"role": "user", "content": "hi"}])

        self.assertEqual(reply, "hello")
        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "https://openrouter.ai/api/v1/chat/completions")
        self.assertEqual(request.get_header("Authorization"), "Bearer test-key")
        body = json.loads(request.data)
        self.assertEqual(body["model"], "test/model")
        self.assertEqual(body["messages"], [{"role": "user", "content": "hi"}])

    @mock.patch("productions.llm.urllib.request.urlopen")
    def test_http_error_becomes_llm_error(self, urlopen):
        urlopen.side_effect = urllib.error.HTTPError(
            llm.URL, 402, "Payment Required", hdrs={}, fp=io.BytesIO(b'{"error": "no credits"}'))
        with self.assertLogs("productions.llm", "ERROR"), self.assertRaisesMessage(LLMError, "HTTP 402"):
            llm.chat([{"role": "user", "content": "hi"}])

    @mock.patch("productions.llm.urllib.request.urlopen")
    def test_network_error_becomes_llm_error(self, urlopen):
        urlopen.side_effect = urllib.error.URLError("no route to host")
        with self.assertLogs("productions.llm", "ERROR"), self.assertRaisesMessage(LLMError, "Could not reach"):
            llm.chat([{"role": "user", "content": "hi"}])

    @mock.patch("productions.llm.urllib.request.urlopen")
    def test_empty_reply_becomes_llm_error(self, urlopen):
        urlopen.return_value = fake_openrouter_response(None)
        with self.assertLogs("productions.llm", "ERROR"), self.assertRaises(LLMError):
            llm.chat([{"role": "user", "content": "hi"}])


class ParseBreakdownTests(SimpleTestCase):
    def test_parses_reply_wrapped_in_code_fence(self):
        data = parse_breakdown(f"Here you go:\n```json\n{GOOD_REPLY}\n```")
        self.assertEqual(data["characters"], [{"name": "MARA", "description": "The lighthouse keeper"}])
        self.assertEqual(data["scenes"][0]["characters"], ["MARA", "TOM"])
        self.assertEqual(data["props"], ["brass scissors", "lantern"])
        self.assertEqual(data["cues"][0]["kind"], "sound")

    def test_drops_malformed_items(self):
        data = parse_breakdown(json.dumps({
            "characters": [{"name": ""}, "not a dict", {"name": "TOM"}],
            "props": ["", None, "oar", {"x": 1}],
            "costumes": "not a list",
            "cues": [{"kind": "pyro", "description": "Flash"}, {"kind": "sound"}],
        }))
        self.assertEqual(data["characters"], [{"name": "TOM", "description": ""}])
        self.assertEqual(data["props"], ["oar"])
        self.assertEqual(data["costumes"], [])
        self.assertEqual(data["scenes"], [])
        self.assertEqual(data["cues"], [{"scene": "", "kind": "other", "description": "Flash"}])

    def test_rejects_non_json(self):
        for reply in ("Sorry, I can't help with that.", "{not json}", "[1, 2]"):
            with self.assertRaises(LLMError):
                parse_breakdown(reply)

    @mock.patch("productions.llm.chat")
    def test_empty_or_huge_script_is_refused_before_calling_llm(self, chat):
        for script in ("   ", "x" * (MAX_SCRIPT_CHARS + 1)):
            with self.assertRaises(LLMError):
                draft_breakdown(script)
        chat.assert_not_called()

    @mock.patch("productions.llm.chat", return_value=GOOD_REPLY)
    def test_sends_script_to_llm(self, chat):
        draft_breakdown("MARA: Hello.")
        messages = chat.call_args.args[0]
        self.assertEqual(messages[0]["role"], "system")
        self.assertEqual(messages[1], {"role": "user", "content": "MARA: Hello."})


class ProductionViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.director = User.objects.create_user("director@example.com", password="pw-for-tests-only")
        self.other = User.objects.create_user("other@example.com", password="pw-for-tests-only")
        self.production = Production.objects.create(owner=self.director, title="Lighthouse", script="MARA: Hello.")
        self.client.login(username="director@example.com", password="pw-for-tests-only")

    def test_pages_require_login(self):
        self.client.logout()
        for url in ("/productions/", "/productions/new/", f"/productions/{self.production.pk}/"):
            self.assertRedirects(self.client.get(url), f"/login/?next={url}")

    def test_list_shows_only_my_productions(self):
        Production.objects.create(owner=self.other, title="Someone else's show")
        r = self.client.get("/productions/")
        self.assertContains(r, "Lighthouse")
        self.assertNotContains(r, "Someone else")

    def test_create_sets_owner(self):
        r = self.client.post("/productions/new/", {"title": "Hamlet", "script": "Who's there?"})
        hamlet = Production.objects.get(title="Hamlet")
        self.assertRedirects(r, f"/productions/{hamlet.pk}/")
        self.assertEqual(hamlet.owner, self.director)

    def test_edit_updates_script(self):
        self.client.post(f"/productions/{self.production.pk}/edit/", {"title": "Lighthouse", "script": "New text"})
        self.production.refresh_from_db()
        self.assertEqual(self.production.script, "New text")

    def test_other_users_cannot_see_or_change_my_production(self):
        self.client.login(username="other@example.com", password="pw-for-tests-only")
        pk = self.production.pk
        self.assertEqual(self.client.get(f"/productions/{pk}/").status_code, 404)
        self.assertEqual(self.client.post(f"/productions/{pk}/edit/", {"title": "x"}).status_code, 404)
        self.assertEqual(self.client.post(f"/productions/{pk}/breakdown/").status_code, 404)

    def test_breakdown_button_disabled_without_ai_key(self):
        r = self.client.get(f"/productions/{self.production.pk}/")
        self.assertContains(r, "AI isn't configured")

    @override_settings(OPENROUTER_API_KEY="test-key", OPENROUTER_MODEL="test/model")
    @mock.patch("productions.llm.chat", return_value=GOOD_REPLY)
    def test_breakdown_is_saved_and_shown(self, chat):
        r = self.client.post(f"/productions/{self.production.pk}/breakdown/", follow=True)
        breakdown = Breakdown.objects.get()
        self.assertEqual(breakdown.production, self.production)
        self.assertEqual(breakdown.model, "test/model")
        self.assertContains(r, "Draft breakdown ready")
        self.assertContains(r, "brass scissors")
        self.assertContains(r, "The lighthouse keeper")

    @override_settings(OPENROUTER_API_KEY="test-key")
    @mock.patch("productions.llm.chat", side_effect=LLMError("The AI service returned an error (HTTP 500)."))
    def test_breakdown_failure_shows_message_and_saves_nothing(self, chat):
        r = self.client.post(f"/productions/{self.production.pk}/breakdown/", follow=True)
        self.assertContains(r, "HTTP 500")
        self.assertFalse(Breakdown.objects.exists())

    def test_breakdown_requires_post(self):
        self.assertEqual(self.client.get(f"/productions/{self.production.pk}/breakdown/").status_code, 405)
