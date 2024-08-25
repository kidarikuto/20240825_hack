from django.contrib.auth.models import AbstractUser
from django.db import models


def image_path(instance, filename):
    return f"images/{instance.username}.{filename.split('.')[-1]}"


class User(AbstractUser):
    email = models.EmailField(blank=True, null=True)
    face_image = models.ImageField(upload_to=image_path, blank=True, null=True, verbose_name='顔写真')
