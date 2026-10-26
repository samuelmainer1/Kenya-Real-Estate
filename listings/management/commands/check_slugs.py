from django.core.management.base import BaseCommand
from listings.models import Listing

class Command(BaseCommand):
    help = 'Check and fix listings with missing slugs'

    def handle(self, *args, **options):
        # Find listings with missing slugs
        missing_slugs = Listing.objects.filter(slug__isnull=True) | Listing.objects.filter(slug='')
        
        if missing_slugs.exists():
            self.stdout.write(f'Found {missing_slugs.count()} listings with missing slugs:')
            for listing in missing_slugs:
                self.stdout.write(f'ID: {listing.id}, Title: {listing.title}')
                # Generate slug by saving
                listing.save()
                self.stdout.write(f'  -> Generated slug: {listing.slug}')
        else:
            self.stdout.write(self.style.SUCCESS('All listings have slugs!'))
        
        # Check if listing with ID 1 exists
        try:
            listing_1 = Listing.objects.get(id=1)
            self.stdout.write(f'Listing ID 1 exists: {listing_1.title} (slug: {listing_1.slug})')
        except Listing.DoesNotExist:
            self.stdout.write(self.style.WARNING('Listing with ID 1 does not exist'))