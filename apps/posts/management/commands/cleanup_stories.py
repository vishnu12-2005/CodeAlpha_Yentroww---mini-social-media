from django.core.management.base import BaseCommand
from django.utils import timezone
from posts.models import Story

class Command(BaseCommand):
    help = 'Deletes expired stories'

    def handle(self, *args, **options):
        now = timezone.now()
        expired = Story.objects.filter(expires_at__lt=now)
        count = expired.count()
        expired.delete()
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} expired stories.'))
