"""Re-copy seeded portfolio images (static/img/works/) into media storage when missing.

The seed migrations copy them once, but a host with an ephemeral disk (Render
without a persistent disk) loses media on every deploy. Run on each start; it
only writes files that are referenced in the DB and absent from storage.
"""
from pathlib import PurePosixPath

from django.conf import settings
from django.core.files import File
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand

from apps.works.models import CaseMedia, CaseStudy

SOURCE = settings.BASE_DIR / "static" / "img" / "works"


class Command(BaseCommand):
    help = "Restore seeded portfolio images missing from media storage."

    def handle(self, *args, **options):
        names = {c.cover.name for c in CaseStudy.objects.exclude(cover="")}
        names |= {m.image.name for m in CaseMedia.objects.exclude(image="")}
        restored = 0
        for name in sorted(names):
            src = SOURCE / PurePosixPath(name).name
            if not src.exists() or default_storage.exists(name):
                continue
            with src.open("rb") as fh:
                default_storage.save(name, File(fh))
            restored += 1
        self.stdout.write(f"Seed media restored: {restored}")
