from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _


def user_has_group_or_permission(user, permission):
    if user.is_superuser:
        return True

    group_names = user.groups.values_list("name", flat=True)
    if not group_names:
        return True

    return user.groups.filter(permissions__codename=permission).exists()


PAGES = [
    {
        "seperator": True,
        "items": [
            {
                "title": _("Home page"),
                "icon": "home",
                "link": reverse_lazy("admin:index"),
            },
        ],
    },
    # Users
    {
        "seperator": True,
        "title": _("Users"),
        "items": [
            {
                "title": _("Groups"),
                "icon": "group_add",
                "link": reverse_lazy("admin:auth_group_changelist"),
                "permission": lambda request: user_has_group_or_permission(
                    request.user, "view_group"
                ),
            },
            {
                "title": _("Users"),
                "icon": "person_add",
                "link": reverse_lazy("admin:auth_user_changelist"),
                "permission": lambda request: user_has_group_or_permission(
                    request.user, "view_user"
                ),
            },
        ],
    },
    # Telegram Bot
    {
        "seperator": True,
        "title": _("Telegram Bot"),
        "items": [
            {
                "title": _("Telegram Users"),
                "icon": "person_add",
                # "link": "en-us/admin/bot/telegramuser/",
                "link": reverse_lazy("admin:bot_telegramuser_changelist"),
                "permission": lambda request: user_has_group_or_permission(
                    request.user, "view_telegramuser"
                ),
            },
            {
                "title": _("News"),
                "icon": "news",
                "link": reverse_lazy("admin:bot_new_changelist"),
                "permission": lambda request: user_has_group_or_permission(
                    request.user, "view_new"
                ),
            },
            {
                "title": _("Feedback"),
                "icon": "feedback",
                "link": reverse_lazy("admin:bot_feedback_changelist"),
                "permission": lambda request: user_has_group_or_permission(
                    request.user, "view_feedback"
                ),
            },
        ],
    },
    # AI
    {
        "seperator": True,
        "title": _("Google (AI)"),
        "items": [
            {
                "title": _("Settings"),
                "icon": "settings",
                "link": reverse_lazy("admin:bot_genaisetting_changelist"),
                "permission": lambda request: user_has_group_or_permission(
                    request.user, "view_genaisettings"
                ),
            },
            {
                "title": _("Histories"),
                "icon": "history",
                "link": reverse_lazy("admin:bot_history_changelist"),
                "permission": lambda request: user_has_group_or_permission(
                    request.user, "view_history"
                ),
            },
        ],
    },
]

TABS = [
    {
        "models": [
            "auth.user",
            "auth.group",
        ],
        "items": [
            {
                "title": _("Users"),
                "link": reverse_lazy("admin:auth_user_changelist"),
            },
            {
                "title": _("Groups"),
                "link": reverse_lazy("admin:auth_group_changelist"),
            },
        ],
    },
]
