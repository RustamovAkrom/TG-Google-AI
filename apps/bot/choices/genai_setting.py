from django.db import models


class GenAIModelChoices(models.TextChoices):
    GEMINI_2_0_FLASH = "gemini-2.0-flash", "Gemini 2.0-Flash"
