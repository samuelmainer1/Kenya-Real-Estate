from django.core.management.base import BaseCommand
from listings.models import Listing

class Command(BaseCommand):
    help = 'Regenerate slugs for listings with missing slugs.'

    def handle(self, *args, **options):
        listings = Listing.objects.filter(slug__isnull=True)
        count = 0
        for listing in listings:
            listing.save()
            count += 1
        self.stdout.write(self.style.SUCCESS(f'Regenerated slugs for {count} listings.'))
