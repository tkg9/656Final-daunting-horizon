from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from productions.models import Membership, Production

SCRIPT = "SCENE 1. Here.\nANNA: Hi.\nSCENE 2. There.\nBEN: Bye."


class ProductionTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.director = User.objects.create_user("dir@example.com", password="pw-dir-123")
        self.outsider = User.objects.create_user("out@example.com", password="pw-out-123")
        self.client.login(username="dir@example.com", password="pw-dir-123")

    def create(self, title="Our Town"):
        self.client.post("/productions/new/", {"title": title})
        return Production.objects.get(title=title)

    def test_login_required(self):
        self.client.logout()
        self.assertEqual(self.client.get("/productions/").status_code, 302)

    def test_creator_becomes_director(self):
        production = self.create()
        self.assertEqual(Membership.objects.get(production=production).role, "director")
        self.assertContains(self.client.get("/productions/"), "Our Town")

    def test_non_members_cannot_see_a_production(self):
        production = self.create()
        self.client.login(username="out@example.com", password="pw-out-123")
        self.assertEqual(self.client.get(f"/productions/{production.pk}/").status_code, 404)

    def test_director_pastes_script_and_gets_scenes(self):
        production = self.create()
        self.client.post(f"/productions/{production.pk}/script/", {"script": SCRIPT})
        self.assertEqual(production.scenes.count(), 2)
        r = self.client.get(f"/productions/{production.pk}/breakdown/")
        self.assertContains(r, "ANNA")
        self.assertContains(r, "BEN")

    def test_replacing_the_script_replaces_scenes(self):
        production = self.create()
        url = f"/productions/{production.pk}/script/"
        self.client.post(url, {"script": SCRIPT})
        self.client.post(url, {"script": "ANNA: Only one scene."})
        self.assertEqual(production.scenes.count(), 1)

    def test_actors_cannot_edit_the_script(self):
        production = self.create()
        Membership.objects.create(production=production, user=self.outsider, role="actor")
        self.client.login(username="out@example.com", password="pw-out-123")
        self.assertEqual(self.client.get(f"/productions/{production.pk}/").status_code, 200)
        self.assertEqual(self.client.post(f"/productions/{production.pk}/script/", {"script": SCRIPT}).status_code, 404)


class SeedDemoTests(TestCase):
    def test_seed_creates_demo_production_once(self):
        call_command("seed")
        call_command("seed")
        production = Production.objects.get(title="Demo production")
        self.assertEqual(production.scenes.count(), 2)
        self.assertEqual(set(production.memberships.values_list("role", flat=True)), {"director", "actor"})
