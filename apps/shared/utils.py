# apps/core/utils.py
from django.utils import timezone
import pytz

def convert_utc_to_local(utc_dt, tz_name="Asia/Tashkent"):
    """
    Конвертирует время UTC в локальную зону.
    """
    if not utc_dt:
        return None
    tz = pytz.timezone(tz_name)
    return utc_dt.astimezone(tz)

def get_client_ip(request):
    """
    Получить IP-адрес клиента.
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip
