import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


class Command(BaseCommand):
    help = 'Compute embeddings for Pet images and store them in MEDIA_ROOT/embeddings'

    def add_arguments(self, parser):
        parser.add_argument('--output', type=str, default=None, help='Output directory (defaults to MEDIA_ROOT/embeddings)')

    def handle(self, *args, **options):
        out = options['output'] or os.path.join(settings.MEDIA_ROOT, 'embeddings')

        # Lazy imports
        try:
            from pets.models import Pet
            from pets.embeddings import build_embeddings
        except Exception as e:
            raise CommandError(f'Import error: {e}')

        qs = Pet.objects.exclude(image__isnull=True).exclude(image='')
        written = build_embeddings(out, qs)
        self.stdout.write(self.style.SUCCESS(f'Wrote {written} embeddings into {out}'))
