from django.core.management.base import BaseCommand
from listings.models import Listing

class Command(BaseCommand):
    help = 'Fix missing slugs for listings.'

    def handle(self, *args, **options):
        listings = Listing.objects.filter(slug__isnull=True)
        count = 0
        for listing in listings:
            listing.save()  # Triggers slug generation in model
            count += 1
        self.stdout.write(self.style.SUCCESS(f'Fixed slugs for {count} listings.'))
