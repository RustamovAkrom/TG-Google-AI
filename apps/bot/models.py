from django.utils.translation import gettext_lazy as _
from django.db import models

from apps.shared.models import BaseAbstractModel
from apps.bot.choices import (
    MessageTypeChoices,
    RoleChoices,
    GenAIModelChoices,
)


class TelegramUser(BaseAbstractModel):

    user_id = models.BigIntegerField(
        verbose_name=_("User ID"), primary_key=True, unique=True
    )
    username = models.CharField(
        verbose_name=_("Username"), max_length=250, blank=True, null=True
    )
    first_name = models.CharField(
        verbose_name=_("First Name"), max_length=250, blank=True, null=True
    )
    last_name = models.CharField(
        verbose_name=_("Last Name"), max_length=250, blank=True, null=True
    )
    language_code = models.CharField(max_length=250, blank=True, null=True)

    email = models.EmailField(
        verbose_name=_("Email Address"), blank=True, null=True
    )  # For Google AI Studio
    access_token = models.CharField(
        verbose_name=_("Access Token (Google AI)"),
        max_length=250,
        blank=True,
        null=True,
    )  # Token from Google AI Studio

    is_active = models.BooleanField(verbose_name=_("Is Active"), default=True)

    def __str__(self):
        return f"{self.username or self.first_name}"

    class Meta:
        db_table = "telegram_users"
        verbose_name = _("Telegram User")
        verbose_name_plural = _("Telegram Users")


class History(BaseAbstractModel):

    telegram_user = models.ForeignKey(
        TelegramUser, on_delete=models.CASCADE, related_name="histories"
    )
    role = models.CharField(
        verbose_name=_("Role"), max_length=20, choices=RoleChoices.choices
    )
    message_type = models.CharField(
        verbose_name=_("Message Type"),
        max_length=20,
        choices=MessageTypeChoices.choices,
        default=MessageTypeChoices.TEXT.value,
    )
    content = models.TextField(verbose_name=_("Content"), blank=True, null=True)
    file = models.FileField(
        verbose_name=_("File"), upload_to="history_files/", blank=True, null=True
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["telegram_user", "created_at"]),
        ]
        db_table = "histories"
        verbose_name = _("History")
        verbose_name_plural = _("Histories")

    def __str__(self):
        return f"{self.telegram_user} ({self.role}) - {self.created_at:%Y-%m-%d %H:%M}"


class New(BaseAbstractModel):

    title = models.CharField(verbose_name=_("Title"), max_length=255)
    text = models.TextField(verbose_name=_("Text"))
    is_published = models.BooleanField(verbose_name=_("Is Published"), default=False)

    def __str__(self):
        return f"{self.title} ({'published' if self.is_published else 'draft'})"

    class Meta:
        db_table = "news"
        verbose_name = _("New")
        verbose_name_plural = _("News")


class GenAISetting(BaseAbstractModel):

    user = models.OneToOneField(
        TelegramUser, on_delete=models.CASCADE, related_name="genai_settings"
    )

    # Main
    model_name = models.CharField(
        verbose_name=_("(Google AI) Model Name"),
        max_length=100,
        choices=GenAIModelChoices.choices,
        default=GenAIModelChoices.GEMINI_2_0_FLASH.value,
    )
    temperature = models.FloatField(verbose_name=_("Temperature"), default=0.5)
    top_k = models.IntegerField(verbose_name=_("Top K"), default=2)
    top_p = models.FloatField(verbose_name=_("Top P"), default=0.5)
    max_output_tokens = models.IntegerField(
        verbose_name=_("Max Output Tokens"), blank=True, null=True
    )
    seed = models.IntegerField(verbose_name=_("Seed"), blank=True, null=True)

    # Arrays and complex settings
    tools = models.JSONField(
        verbose_name=_("Tools"), default=list
    )  # [{'type': 'url_context'}, {'type': 'google_search'}]
    safety_settings = models.JSONField(
        verbose_name=_("Safety Settings"), default=list
    )  # [{'category': '', 'threshold': ''}]

    def __str__(self):
        return f"GenAI Settings for {self.user.user_id}"

    class Meta:
        db_table = "genai_ai_settings"
        verbose_name = _("GenAI Setting")
        verbose_name_plural = _("GenAI Settings")
