from django.core.management.base import BaseCommand
from listings.models import Listing

class Command(BaseCommand):
    help = 'Geocode all listings that are missing coordinates'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Re-geocode all listings, even those with existing coordinates',
        )

    def handle(self, *args, **options):
        if options['force']:
            listings = Listing.objects.all()
            self.stdout.write('Re-geocoding ALL listings...')
        else:
            listings = Listing.objects.filter(
                models.Q(latitude__isnull=True) | models.Q(longitude__isnull=True)
            )
            self.stdout.write(f'Geocoding {listings.count()} listings without coordinates...')
        
        success_count = 0
        for listing in listings:
            if options['force']:
                listing.latitude = None
                listing.longitude = None
            
            if listing.auto_geocode():
                listing.save()
                success_count += 1
                self.stdout.write(f'✓ Geocoded: {listing.title}')
            else:
                self.stdout.write(f'✗ Failed: {listing.title}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully geocoded {success_count} listings')
        )