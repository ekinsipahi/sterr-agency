"""Check one or more languages of the follower pages against the English source:
    python manage.py check_growth_copy de nl
Imports only those languages' files, so it works while other translations are in progress."""
from django.core.management.base import BaseCommand, CommandError

from apps.growth.validate import check


class Command(BaseCommand):
    help = "Validate follower-page translations (structure, meta lengths, wording, keywords)."
    requires_system_checks = []

    def add_arguments(self, parser):
        parser.add_argument("codes", nargs="+")

    def handle(self, *args, **opts):
        failed = False
        for code in opts["codes"]:
            problems = check(code)
            for p in problems:
                self.stdout.write(p)
            self.stdout.write(f"{code}: {'OK' if not problems else f'{len(problems)} problem(s)'}")
            failed = failed or bool(problems)
        if failed:
            raise CommandError("translation check failed")
