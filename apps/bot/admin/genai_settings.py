from django.contrib import admin
from unfold.admin import ModelAdmin
from apps.bot.models import GenAISetting


@admin.register(GenAISetting)
class GenAISettingAdmin(ModelAdmin):
    pass
