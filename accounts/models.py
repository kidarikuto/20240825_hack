import os

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver


def image_path(instance, filename):
    return f"images/{instance.username}.{filename.split('.')[-1]}"


class User(AbstractUser):
    email = models.EmailField(blank=True, null=True)
    face_image = models.ImageField(upload_to=image_path, blank=True, null=True, verbose_name="顔写真")


# ユーザーが削除されたときに顔写真も削除
@receiver(pre_delete, sender=User)
def delete_face_image(sender, instance, **kwargs):
    if instance.face_image:
        if os.path.isfile(instance.face_image.path):
            os.remove(instance.face_image.path)
