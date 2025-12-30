import os
from django.core.management.base import BaseCommand, CommandError
from django.core.files import File
from django.conf import settings


class Command(BaseCommand):
    help = 'Ingest images from a directory into Pet entries (computes phash)'

    def add_arguments(self, parser):
        parser.add_argument('directory', type=str, help='Directory containing images to ingest')
        parser.add_argument('--owner', type=str, default='admin', help='Username of owner to assign')
        parser.add_argument('--status', type=str, default='available', help='Pet status (lost/found/available)')

    def handle(self, *args, **options):
        directory = options['directory']
        owner_username = options['owner']
        status = options['status']

        if not os.path.isdir(directory):
            raise CommandError(f"Directory not found: {directory}")

        # Lazy imports to avoid Django setup issues
        from django.contrib.auth import get_user_model
        from pets.models import Pet
        from PIL import Image
        import imagehash

        User = get_user_model()
        try:
            owner = User.objects.get(username=owner_username)
        except User.DoesNotExist:
            raise CommandError(f"User not found: {owner_username}")

        created = 0
        for root, _, files in os.walk(directory):
            for fname in files:
                if not fname.lower().endswith(('.jpg', '.jpeg', '.png')):
                    continue
                full = os.path.join(root, fname)
                name = os.path.splitext(fname)[0]

                pet = Pet(owner=owner, name=name[:100], status=status)
                # Save so we get an ID and can attach image
                pet.save()
                with open(full, 'rb') as f:
                    django_file = File(f)
                    pet.image.save(fname, django_file, save=True)

                # compute phash
                try:
                    with Image.open(pet.image.path) as im:
                        h = imagehash.phash(im)
                        pet.image_hash = h.__str__()
                        pet.save()
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Failed to hash {fname}: {e}"))

                created += 1

        self.stdout.write(self.style.SUCCESS(f"Ingested {created} images from {directory}"))
