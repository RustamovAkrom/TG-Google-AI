from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.bot.models import TelegramUser, GenAISetting


@receiver(post_save, sender=TelegramUser)
def create_user_settings(sender, instance, created, **kwargs):
    if created:
        GenAISetting.objects.create(
            user=instance,
            tools=[{"type": "url_context"}, {"type": "google_search"}],
            safety_settings=[
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_ONLY_HIGH",
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_ONLY_HIGH",
                },
            ],
        )
