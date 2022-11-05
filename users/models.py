from django.db import models
from django.contrib.auth.models import AbstractUser, Group
import uuid

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from django.contrib.auth.models import User

from .utils import generate_code, generate_digits_code

class Verification(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    code = models.CharField(max_length=6, default=generate_digits_code, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_valid = models.BooleanField(default=True)
    is_used = models.BooleanField(default=False)
    channels = [
        ("EMAIL", "EMAIL"),
        ("ALL", "ALL"),
    ]
    channel = models.CharField(max_length=30, default="ALL", choices=channels)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.user.email}"


# @receiver(post_save, sender=Verification)
# def post_save_verification(sender, instance=None, created=False, **kwargs):
#     from users.tasks.tasks_verification import schedule_expiration
#     if created and instance:
#         schedule_expiration.delay(str(instance.id))