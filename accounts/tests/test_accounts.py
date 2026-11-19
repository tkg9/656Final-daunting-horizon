from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from productions.demo import DEMO_TITLE
from productions.models import Production


class SeedTests(TestCase):
    def test_seed_creates_loginable_accounts_and_is_rerunnable(self):
        call_command("seed", stdout=StringIO())
        call_command("seed", stdout=StringIO())
        self.assertEqual(get_user_model().objects.count(), 2)
        self.assertTrue(self.client.login(username="admin@example.com", password="stage-door-lantern"))
        self.assertTrue(self.client.login(username="member@example.com", password="curtain-call-rope"))

    def test_seed_creates_demo_data_once_and_keeps_edits(self):
        call_command("seed", stdout=StringIO())
        member = get_user_model().objects.get(username="member@example.com")
        demo = member.productions.get(title=DEMO_TITLE)
        self.assertIn("MARA", demo.script)
        demo.script = "edited"
        demo.save()

        call_command("seed", stdout=StringIO())
        self.assertEqual(Production.objects.filter(title=DEMO_TITLE).count(), 2)  # one per grader
        demo.refresh_from_db()
        self.assertEqual(demo.script, "edited")

    def test_admin_account_can_open_admin(self):
        call_command("seed", stdout=StringIO())
        self.client.login(username="admin@example.com", password="stage-door-lantern")
        self.assertEqual(self.client.get("/admin/").status_code, 200)


class AuthPageTests(TestCase):
    def test_login_page_loads(self):
        self.assertEqual(self.client.get("/login/").status_code, 200)

    def test_home_page_loads(self):
        r = self.client.get("/")
        self.assertContains(r, "StageCraft")
        self.assertContains(r, 'name="viewport"')

    def test_signup_creates_account_and_logs_in(self):
        r = self.client.post("/signup/", {
            "username": "director@example.com",
            "password1": "a-long-stage-password",
            "password2": "a-long-stage-password",
        })
        self.assertRedirects(r, "/productions/")
        self.assertTrue(get_user_model().objects.filter(username="director@example.com").exists())
        self.assertEqual(self.client.get("/productions/").status_code, 200)

    def test_signup_rejects_mismatched_passwords(self):
        r = self.client.post("/signup/", {
            "username": "director@example.com",
            "password1": "a-long-stage-password",
            "password2": "something-else-entirely",
        })
        self.assertEqual(r.status_code, 200)
        self.assertFalse(get_user_model().objects.exists())

    def test_logout_returns_home(self):
        get_user_model().objects.create_user("a@example.com", password="pw-not-used-elsewhere")
        self.client.login(username="a@example.com", password="pw-not-used-elsewhere")
        self.assertRedirects(self.client.post("/logout/"), "/")
