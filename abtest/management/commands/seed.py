"""Create the grader accounts and a demo production. Safe to rerun.

Run: python manage.py seed
Passwords come from SEED_ADMIN_PASSWORD / SEED_MEMBER_PASSWORD when set.
"""
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from productions import script
from productions.models import Membership, Production, Scene

DEMO_SCRIPT = """SCENE 1. A rehearsal room.
MAYA: Places, everyone. We start from the top.
THEO: Do we have the ladder yet?
MAYA: Not until Thursday.

SCENE 2. The empty stage, later.
THEO: The light on stage left keeps flickering.
JUNE: I'll tell the crew before the run.
"""

ACCOUNTS = [
    ("admin@example.com", "SEED_ADMIN_PASSWORD", "stage-door-lantern", True),
    ("member@example.com", "SEED_MEMBER_PASSWORD", "curtain-call-rope", False),
]


class Command(BaseCommand):
    help = "Create or update the grader accounts."

    def handle(self, *args, **options):
        User = get_user_model()
        for email, env_var, default_password, is_admin in ACCOUNTS:
            user, created = User.objects.get_or_create(username=email, defaults={"email": email})
            user.set_password(os.environ.get(env_var, default_password))
            user.is_staff = user.is_superuser = is_admin
            user.save()
            self.stdout.write(f"{'created' if created else 'updated'} {email}")
        self.seed_demo(User)

    def seed_demo(self, User):
        admin = User.objects.get(username="admin@example.com")
        member = User.objects.get(username="member@example.com")
        production, created = Production.objects.get_or_create(title="Demo production", defaults={"created_by": admin})
        Membership.objects.get_or_create(production=production, user=admin, defaults={"role": "director"})
        Membership.objects.get_or_create(production=production, user=member, defaults={"role": "actor"})
        if created:
            Scene.objects.bulk_create(Scene(production=production, **s) for s in script.split_scenes(DEMO_SCRIPT))
        self.stdout.write(f"{'created' if created else 'kept'} Demo production")
