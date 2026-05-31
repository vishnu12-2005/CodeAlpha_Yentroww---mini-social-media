from django.core.management.base import BaseCommand
from social.models import WeeklyLeaderboard

class Command(BaseCommand):
    help = 'Resets the leaderboard (called weekly)'

    def handle(self, *args, **options):
        # We don't delete past leaderboards if we want history, but the prompt says reset.
        # So we just clear the current active ones or do nothing since update_leaderboard 
        # creates it for the new week automatically. For full reset we can just clear all.
        count, _ = WeeklyLeaderboard.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'Successfully reset leaderboard ({count} records deleted).'))
