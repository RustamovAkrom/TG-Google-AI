from django.contrib import admin
from unfold.admin import ModelAdmin
from apps.bot.models import History


@admin.register(History)
class HistoryAdmin(ModelAdmin):
    pass

