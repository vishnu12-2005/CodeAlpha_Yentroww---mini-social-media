from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from social.models import WeeklyLeaderboard
from django.utils import timezone
from datetime import timedelta
from posts.models import Reaction
from django.contrib.contenttypes.models import ContentType
from posts.models import Post

class Command(BaseCommand):
    help = 'Updates the weekly leaderboard'

    def handle(self, *args, **options):
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)

        users = User.objects.all()
        content_type = ContentType.objects.get_for_model(Post)
        
        leaderboard_data = []
        for user in users:
            post_ids = user.posts.values_list('id', flat=True)
            y_count = Reaction.objects.filter(
                content_type=content_type, 
                object_id__in=post_ids, 
                reaction_type='yentroww',
                created_at__date__gte=week_start,
                created_at__date__lte=week_end
            ).count()
            
            if y_count > 0:
                leaderboard_data.append({'user': user, 'count': y_count})

        # Sort by count desc
        leaderboard_data.sort(key=lambda x: x['count'], reverse=True)

        # Clear existing for this week
        WeeklyLeaderboard.objects.filter(week_start=week_start, week_end=week_end).delete()

        # Create new
        rank = 1
        for data in leaderboard_data:
            WeeklyLeaderboard.objects.create(
                user=data['user'],
                week_start=week_start,
                week_end=week_end,
                yentroww_count=data['count'],
                rank=rank
            )
            rank += 1
            
        self.stdout.write(self.style.SUCCESS(f'Successfully updated leaderboard for week {week_start} to {week_end}'))
