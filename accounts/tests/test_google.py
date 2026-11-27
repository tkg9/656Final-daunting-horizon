from unittest import mock
from urllib.parse import parse_qs, urlparse

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

INFO = {"email": "Ana@Example.com", "email_verified": True, "given_name": "Ana", "family_name": "Lee"}


@override_settings(GOOGLE_CLIENT_ID="cid", GOOGLE_CLIENT_SECRET="secret")
class GoogleLoginTests(TestCase):
    def start(self, next_url=""):
        r = self.client.get("/auth/google/", {"next": next_url} if next_url else {})
        self.assertEqual(r.status_code, 302)
        query = parse_qs(urlparse(r["Location"]).query)
        self.assertEqual(query["redirect_uri"], ["http://testserver/auth/google/callback/"])
        return query["state"][0]

    def finish(self, state, info=INFO):
        with mock.patch("accounts.views._fetch_userinfo", return_value=info):
            return self.client.get("/auth/google/callback/", {"state": state, "code": "abc"})

    def test_new_user_is_created_and_logged_in(self):
        r = self.finish(self.start())
        self.assertRedirects(r, "/", fetch_redirect_response=False)
        user = get_user_model().objects.get(username="ana@example.com")
        self.assertFalse(user.has_usable_password())
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.pk)

    def test_existing_user_is_matched_by_email(self):
        user = get_user_model().objects.create_user("ana@example.com", password="pw-123-abc")
        self.finish(self.start())
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.pk)
        self.assertEqual(get_user_model().objects.count(), 1)

    def test_bad_state_is_rejected(self):
        self.start()
        r = self.finish("forged")
        self.assertRedirects(r, "/login/", fetch_redirect_response=False)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_unverified_email_is_rejected(self):
        self.finish(self.start(), {**INFO, "email_verified": False})
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_next_is_kept_but_offsite_next_is_dropped(self):
        self.assertRedirects(self.finish(self.start("/productions/")), "/productions/", fetch_redirect_response=False)
        self.client.logout()
        self.assertRedirects(self.finish(self.start("https://evil.example/")), "/", fetch_redirect_response=False)

    @override_settings(GOOGLE_CLIENT_ID="")
    def test_disabled_without_client_id(self):
        self.assertEqual(self.client.get("/auth/google/").status_code, 404)
        self.assertNotContains(self.client.get("/login/"), "Google")
