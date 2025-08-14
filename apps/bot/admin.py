from django.contrib import admin
from .models import TelegramUser, History, GenAISettings


admin.site.register([TelegramUser, History, GenAISettings])
# Register your models here.
