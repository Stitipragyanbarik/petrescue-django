import os
import tarfile
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Download and extract Oxford-IIIT Pet Dataset (images).'

    def add_arguments(self, parser):
        parser.add_argument('dest', type=str, help='Destination directory to extract images into')

    def handle(self, *args, **options):
        dest = options['dest']
        os.makedirs(dest, exist_ok=True)

        url = 'https://www.robots.ox.ac.uk/~vgg/data/pets/data/images.tar.gz'
        archive_path = os.path.join(dest, 'images.tar.gz')

        try:
            import requests
        except Exception:
            raise CommandError('The `requests` package is required to download the dataset. Install it with `pip install requests`')

        self.stdout.write(f'Downloading Oxford-IIIT Pet images to {archive_path} ...')
        try:
            r = requests.get(url, stream=True, timeout=60)
            r.raise_for_status()
            with open(archive_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        except Exception as e:
            raise CommandError(f'Download failed: {e}')

        self.stdout.write('Extracting images...')
        try:
            with tarfile.open(archive_path, 'r:gz') as tar:
                tar.extractall(path=dest)
        except Exception as e:
            raise CommandError(f'Extraction failed: {e}')

        self.stdout.write(self.style.SUCCESS(f'Oxford pet images downloaded and extracted to {dest}'))
