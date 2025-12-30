from django.core.management.base import BaseCommand
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Check that Pet.image files exist on disk and report missing files.'

    def handle(self, *args, **options):
        try:
            from pets.models import Pet
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error importing Pet model: {e}'))
            return

        total = 0
        missing = []
        with_hash = 0
        for pet in Pet.objects.all():
            total += 1
            if pet.image:
                with_hash += 1
                try:
                    path = pet.image.path
                except Exception:
                    path = None
                if not path or not os.path.exists(path):
                    missing.append((pet.id, getattr(pet, 'name', ''), path))

        if not missing:
            self.stdout.write(self.style.SUCCESS(f'Checked {total} pets ({with_hash} with images): no missing image files.'))
        else:
            self.stdout.write(self.style.WARNING(f'Checked {total} pets ({with_hash} with images): found {len(missing)} missing image file(s):'))
            for pid, name, path in missing:
                self.stdout.write(f' - Pet id={pid} name="{name}" expected path={path}')

            self.stdout.write('')
            self.stdout.write('Suggestions:')
            self.stdout.write(' - If you moved/removed media files, restore them under MEDIA_ROOT (settings.MEDIA_ROOT).')
            self.stdout.write(' - To clear broken image references, run a script to set pet.image = None for the listed ids.')
