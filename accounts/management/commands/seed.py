"""Create the grader accounts and demo data. Safe to rerun.

Run: python manage.py seed (also run by build.sh on every deploy, so it
recreates everything after a database reset).
Passwords come from SEED_ADMIN_PASSWORD / SEED_MEMBER_PASSWORD when set.
"""
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from productions.demo import create_demo_data

ACCOUNTS = [
    ("admin@example.com", "SEED_ADMIN_PASSWORD", "stage-door-lantern", True),
    ("member@example.com", "SEED_MEMBER_PASSWORD", "curtain-call-rope", False),
]


class Command(BaseCommand):
    help = "Create or update the grader accounts and their demo data."

    def handle(self, *args, **options):
        User = get_user_model()
        for email, env_var, default_password, is_admin in ACCOUNTS:
            user, created = User.objects.get_or_create(username=email, defaults={"email": email})
            user.set_password(os.environ.get(env_var, default_password))
            user.is_staff = user.is_superuser = is_admin
            user.save()
            self.stdout.write(f"{'created' if created else 'updated'} {email}")
            if create_demo_data(user):
                self.stdout.write(f"  added demo production for {email}")
