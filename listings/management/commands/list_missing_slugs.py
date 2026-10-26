from django.core.management.base import BaseCommand
from listings.models import Listing

class Command(BaseCommand):
    help = 'List all listings with missing or empty slugs.'

    def handle(self, *args, **options):
        missing = Listing.objects.filter(slug__isnull=True) | Listing.objects.filter(slug='')
        if missing.exists():
            self.stdout.write('Listings with missing or empty slugs:')
            for l in missing:
                self.stdout.write(f'ID: {l.id}, Title: {l.title}, Published: {l.is_published}')
        else:
            self.stdout.write(self.style.SUCCESS('No listings with missing or empty slugs.'))
