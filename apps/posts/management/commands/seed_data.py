import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from posts.models import Post, Reel, Story, Reaction, Comment, Tag, PostTag
from users.models import Profile, Follow
from social.models import WeeklyLeaderboard
from messaging.models import Conversation, Message
from notifications.models import Notification
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from datetime import timedelta

SAMPLE_USERNAMES = [
    'teluguVibe', 'chillBro_99', 'hyderabad_raja', 'biryani_king',
    'memes_telugu', 'chill_macha', 'funWithRaju', 'coding_hero',
    'night_owl_dev', 'foodie_queen', 'travel_adda', 'dance_fever',
    'music_mantra', 'art_spark', 'gamer_pro', 'fitness_freak',
    'book_worm42', 'movie_buff', 'cricket_fan01', 'tech_guru',
    'photo_magic', 'fashion_diva', 'nature_lover', 'sky_gazer',
    'chef_special', 'comedy_king', 'drama_queen', 'poet_heart',
    'singer_soul', 'rider_life', 'yoga_peace', 'surf_wave',
    'star_dust', 'moon_child', 'fire_blaze', 'ice_cool',
    'thunder_bolt', 'rainbow_ray', 'ocean_deep', 'mountain_high',
    'urban_style', 'retro_vibes', 'neon_glow', 'pixel_art',
    'beat_master', 'word_smith', 'dream_catcher', 'soul_searcher',
    'mind_bender', 'wave_runner',
]

SAMPLE_BIOS = [
    "Living life one yentroww at a time 😯",
    "Hyderabadi born, globally known 🌍",
    "Just here for the biryani reviews 🍗",
    "Code by day, memes by night 💻",
    "Making people go yentroww since 2024 🔥",
    "Cricket + Chai = Life ☕🏏",
    "Professional overthinker 🧠",
    "Spreading smiles, one post at a time 😄",
    "Travel | Food | Vibes ✈️🍔✨",
    "Born to stand out, not fit in 💎",
    "Director of doing nothing 🎬",
    "404: Bio not found 🤷",
    "In a serious relationship with food 🍕",
    "Keep calm and say yentroww 😯",
    "Life is short, make every post count 📸",
]

SAMPLE_CAPTIONS = [
    "Just saw something incredible... yentroww?! 😯🔥",
    "This view is absolutely insane! Who else loves sunsets? 🌅",
    "Monday motivation: Keep going, keep growing 💪",
    "Tag someone who needs to see this! 👇",
    "POV: When the biryani hits different 🍗😍",
    "Late night coding sessions be like... 💻☕",
    "Throwback to this amazing day! #memories",
    "When you realize tomorrow is Monday 😭",
    "Celebrating small wins today! 🎉🥳",
    "This weather is making me feel some type of way 🌧️",
    "New hobby unlocked! What do you think? 🎨",
    "Grateful for this beautiful life 🙏✨",
    "Can someone explain how it's already June?! 📅",
    "That feeling when your code works on first try 🎯",
    "Exploring new places, finding new stories 🗺️",
    "Who else is a night owl? 🦉🌙",
    "Plot twist: Life is actually good right now 🥰",
    "Comfort zone? Don't know her 💅",
    "Currently accepting applications for travel buddy ✈️",
    "Just posted this to make you go yentroww 😯",
    "Weekend vibes only 🎶🍕",
    "Learning something new every single day 📚",
    "This is my sign to take a break ☕",
    "Obsessed with this aesthetic 🎨✨",
    "They said it couldn't be done... watch me 🔥",
    "Simple pleasures, extraordinary moments 💫",
    "Chai + rain = perfection 🌧️☕",
    "Story time! So this happened today... 😱",
    "Manifesting great things for all of us 🌟",
    "Still can't believe this is real 😯🤯",
    "Find someone who looks at you like I look at food 🍔❤️",
    "Adventure is out there! 🏔️🌈",
    "My brain has too many tabs open 🧠💥",
    "Proof that I do actually go outside sometimes 🌳",
    "This is what happiness looks like 😊",
    "Making memories worth remembering 📸💛",
    "New day, new opportunities, same amazing me 💁",
    "Just here, living my best life ✌️",
    "Coffee first, adulting second ☕😴",
    "Tell me your favorite movie without telling me 🎬",
    "Sundays are for self-care and zero productivity 🛁",
    "Currently running on 3 hours of sleep and vibes 😅",
    "This week's mood: unstoppable 🚀",
    "Sending good energy to everyone reading this ✨",
    "Namaste from a random beautiful spot 🙏🌸",
    "Who's up for a spontaneous road trip? 🚗💨",
    "Hot take: Pani Puri > Everything else 🤤",
    "Started from the bottom, now we're still here but vibing 😂",
    "That awkward moment when you wave at someone and they don't see you 🙈",
    "Dropping this here and walking away 😎💣",
    "Today's agenda: absolutely nothing productive 🛋️",
    "Can we normalize taking naps at work? 😴💼",
    "Weekend calories don't count, right? 🍰",
    "Scrolling through my own photos because I'm my own biggest fan 📱💕",
    "One more episode... said me 4 hours ago 📺",
    "Living for moments that make you go YENTROWW 😯🔥",
    "This post is brought to you by procrastination™ 📝",
    "If lost, please return to nearest food stall 🍜",
    "Trying to be a morning person... attempt #847 ☀️😩",
    "Main character energy activated 🎭✨",
]

SAMPLE_COMMENTS = [
    "This is fire! 🔥🔥",
    "Yentroww! 😯",
    "Haha love this 😂",
    "Need more content like this!",
    "Absolutely stunning 😍",
    "You're killing it! 💪",
    "This made my day 🥰",
    "Tag me next time! 😤",
    "Can't stop laughing 😂😂",
    "Goals! 🙌",
    "Wow, just wow! 🤩",
    "So relatable 😅",
    "Best post today! 👏",
    "Drop the location! 📍",
    "This is everything 💯",
]


class Command(BaseCommand):
    help = 'Seed database with 50+ sample users, posts, reactions, and more'

    def handle(self, *args, **options):
        self.stdout.write("🚀 Starting seed data injection...")

        # 1. Create Users
        created_users = []
        for i, uname in enumerate(SAMPLE_USERNAMES):
            user, created = User.objects.get_or_create(
                username=uname,
                defaults={
                    'email': f'{uname}@yentroww.com',
                    'first_name': uname.replace('_', ' ').title()[:30],
                }
            )
            if created:
                user.set_password('yentroww123')
                user.save()
                # Update profile
                profile = user.profile
                profile.bio = random.choice(SAMPLE_BIOS)
                profile.account_type = random.choice(['public', 'public', 'public', 'private'])
                profile.save()
                created_users.append(user)
                self.stdout.write(f"  ✅ Created user: {uname}")
            else:
                created_users.append(user)

        all_users = list(User.objects.all())
        self.stdout.write(f"\n📊 Total users: {len(all_users)}")

        # 2. Create Follow relationships
        follow_count = 0
        for user in all_users:
            # Each user follows 5-15 random others
            num_follows = random.randint(5, min(15, len(all_users) - 1))
            others = [u for u in all_users if u != user]
            to_follow = random.sample(others, min(num_follows, len(others)))
            for target in to_follow:
                _, created = Follow.objects.get_or_create(follower=user, following=target)
                if created:
                    follow_count += 1
        self.stdout.write(f"🤝 Created {follow_count} follow relationships")

        # 3. Create Posts (text-only since no media files)
        post_count = 0
        for caption in SAMPLE_CAPTIONS:
            user = random.choice(all_users)
            post, created = Post.objects.get_or_create(
                user=user,
                caption=caption,
                defaults={
                    'media_type': 'text',
                    'visibility': 'public',
                }
            )
            if created:
                post_count += 1
        self.stdout.write(f"📝 Created {post_count} posts")

        # 4. Create Reactions on posts
        all_posts = list(Post.objects.all())
        content_type = ContentType.objects.get_for_model(Post)
        reaction_count = 0
        for post in all_posts:
            # Each post gets 3-15 random reactions
            num_reactions = random.randint(3, min(15, len(all_users)))
            reactors = random.sample(all_users, num_reactions)
            for reactor in reactors:
                rtype = random.choice(['yentroww', 'yentroww', 'yentroww', 'abboww', 'sarlee'])
                _, created = Reaction.objects.get_or_create(
                    user=reactor,
                    content_type=content_type,
                    object_id=post.id,
                    defaults={'reaction_type': rtype}
                )
                if created:
                    reaction_count += 1
        self.stdout.write(f"😯 Created {reaction_count} reactions")

        # 5. Create Comments
        comment_count = 0
        for post in random.sample(all_posts, min(40, len(all_posts))):
            num_comments = random.randint(1, 5)
            commenters = random.sample(all_users, min(num_comments, len(all_users)))
            for commenter in commenters:
                Comment.objects.create(
                    user=commenter,
                    post=post,
                    text=random.choice(SAMPLE_COMMENTS)
                )
                comment_count += 1
        self.stdout.write(f"💬 Created {comment_count} comments")

        # 6. Create Leaderboard
        now = timezone.now()
        week_start = (now - timedelta(days=now.weekday())).date()
        week_end = week_start + timedelta(days=6)

        # Calculate top users by yentroww reactions received
        user_scores = []
        for user in all_users:
            post_ids = user.posts.values_list('id', flat=True)
            y_count = Reaction.objects.filter(
                content_type=content_type,
                object_id__in=post_ids,
                reaction_type='yentroww'
            ).count()
            if y_count > 0:
                user_scores.append((user, y_count))

        user_scores.sort(key=lambda x: x[1], reverse=True)
        for rank, (user, score) in enumerate(user_scores[:20], 1):
            WeeklyLeaderboard.objects.update_or_create(
                user=user,
                week_start=week_start,
                week_end=week_end,
                defaults={'yentroww_count': score, 'rank': rank}
            )
        self.stdout.write(f"🏆 Created leaderboard with {min(20, len(user_scores))} entries")

        # 7. Create sample conversations and messages
        conv_count = 0
        msg_count = 0
        sample_messages = [
            "Hey! What's up? 😊",
            "Did you see that post?! Yentroww! 😯",
            "Haha yes! So funny 😂",
            "We should meet up sometime!",
            "Check out this cool thing I found",
            "Good morning! ☀️",
            "Movie tonight? 🎬",
            "That was amazing!",
            "Can't believe it 🤯",
            "Let's plan something for the weekend!",
        ]
        pairs_created = set()
        for _ in range(25):
            u1, u2 = random.sample(all_users, 2)
            pair_key = tuple(sorted([u1.id, u2.id]))
            if pair_key in pairs_created:
                continue
            pairs_created.add(pair_key)

            conv = Conversation.objects.create()
            conv.participants.add(u1, u2)
            conv_count += 1

            num_msgs = random.randint(2, 6)
            for j in range(num_msgs):
                sender = random.choice([u1, u2])
                Message.objects.create(
                    conversation=conv,
                    sender=sender,
                    text=random.choice(sample_messages)
                )
                msg_count += 1

        self.stdout.write(f"📨 Created {conv_count} conversations with {msg_count} messages")

        # 8. Create some notifications
        notif_count = 0
        for _ in range(30):
            sender = random.choice(all_users)
            recipient = random.choice([u for u in all_users if u != sender])
            ntype = random.choice(['reaction', 'comment', 'follow', 'mention'])
            Notification.objects.create(
                recipient=recipient,
                sender=sender,
                notif_type=ntype
            )
            notif_count += 1
        self.stdout.write(f"🔔 Created {notif_count} notifications")

        self.stdout.write(self.style.SUCCESS(
            f"\n🎉 DONE! Seeded: {len(all_users)} users, {Post.objects.count()} posts, "
            f"{Reaction.objects.count()} reactions, {Comment.objects.count()} comments, "
            f"{conv_count} conversations"
        ))
