from django.core.management.base import BaseCommand
from django.utils import timezone
from blog.models import Blog

class Command(BaseCommand):
    help = 'Publish blogs that are scheduled for the current time or earlier'

    def handle(self, *args, **options):
        now = timezone.now()
        scheduled_blogs = Blog.objects.filter(
            scheduled_at__lte=now,
            published=False
        )
        
        count = 0
        for blog in scheduled_blogs:
            blog.published = True
            blog.save()
            count += 1
            self.stdout.write(
                self.style.SUCCESS(f'Published: {blog.title}')
            )
        
        if count == 0:
            self.stdout.write('No blogs to publish at this time.')
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully published {count} blog(s)')
            )