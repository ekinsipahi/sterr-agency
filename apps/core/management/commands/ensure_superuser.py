"""Create the admin user from DJANGO_SUPERUSER_USERNAME / _EMAIL / _PASSWORD if it
doesn't exist yet. Safe to run on every deploy (hosts without a shell, e.g. Render
free plan). Never changes an existing user's password."""
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create the superuser from environment variables when missing."

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
        if not username or not password:
            self.stdout.write("DJANGO_SUPERUSER_USERNAME/PASSWORD not set; skipping.")
            return
        User = get_user_model()
        if User.objects.filter(username=username).exists():
            self.stdout.write(f"Superuser '{username}' exists.")
            return
        User.objects.create_superuser(username, os.environ.get("DJANGO_SUPERUSER_EMAIL", ""), password)
        self.stdout.write(f"Superuser '{username}' created.")
