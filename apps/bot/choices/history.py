from django.db import models


class MessageTypeChoices(models.TextChoices):
    TEXT = 'text', "TEXT"
    IMAGE = 'image', "Image"
    DOCUMENT = 'document', "Document"
    AUDIO = 'audio', 'Audio'
    VIDEO = 'video', 'Video'


class RoleChoices(models.TextChoices):
    USER = 'user', "User"
    MODEL = 'model', "Model"
