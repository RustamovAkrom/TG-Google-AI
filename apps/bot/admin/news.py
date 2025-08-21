from django.contrib import admin
from unfold.admin import ModelAdmin
from apps.bot.models import New


@admin.register(New)
class NewAdmin(ModelAdmin):
    pass
