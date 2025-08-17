from django.contrib import admin
from .models import TelegramUser, History, GenAISetting, New


admin.site.register([TelegramUser, History, New, GenAISetting])
# Register your models here.
