from django.contrib import admin
from unfold.admin import ModelAdmin
from apps.bot.models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(ModelAdmin):
    pass
