from django.contrib import admin
from .models import TelegramUser, History


admin.site.register([TelegramUser, History])
# Register your models here.
