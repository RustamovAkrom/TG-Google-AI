from django.contrib import admin
from .models import TelegramUser, History, GenAISetting, New, Feedback


admin.site.register([TelegramUser, History, New, GenAISetting, Feedback])
# Register your models here.
