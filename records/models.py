from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()

ACTION_CHOICES = (
    ('IN', '入室'),
    ('OUT', '退室'),
)

class EntryExitLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=3, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
