from django.db import models
from django.utils import timezone
from apps.shared.models import BaseAbstractModel


class TelegramUser(BaseAbstractModel):
    user_id = models.BigIntegerField(primary_key=True, unique=True)
    username = models.CharField(max_length=250, blank=True, null=True)
    first_name = models.CharField(max_length=250, blank=True, null=True)
    last_name = models.CharField(max_length=250, blank=True, null=True)
    language_code = models.CharField(max_length=250, blank=True, null=True)

    email = models.EmailField(blank=True, null=True) # For Google AI Studio
    access_token = models.CharField(max_length=250, blank=True, null=True) # Token from Google AI Studio

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.username or self.first_name}"
    
    class Meta:
        verbose_name = "Telegram User"
        verbose_name_plural = "Telegram Users"

    
class History(BaseAbstractModel):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('model', 'Model'),
    ]

    MESSAGE_TYPE_CHOICES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('document', 'Document'),
        ('audio', 'Audio'),
        ('video', 'Video'),
    ]

    telegram_user = models.ForeignKey(
        TelegramUser,
        on_delete=models.CASCADE,
        related_name="histories"
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )
    message_type = models.CharField(
        max_length=20,
        choices=MESSAGE_TYPE_CHOICES,
        default='text'
    )
    content = models.TextField(blank=True, null=True)
    file = models.FileField(
        upload_to="history_files/",
        blank=True,
        null=True
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['telegram_user', 'created_at']),
        ]

    def __str__(self):
        return f"{self.telegram_user} ({self.role}) - {self.created_at:%Y-%m-%d %H:%M}"
    

class News(BaseAbstractModel):
    title = models.CharField(max_length=255)
    text = models.TextField()
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} ({'published' if self.is_published else 'draft'})"
