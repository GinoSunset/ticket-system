from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.shortcuts import reverse
from django.conf import settings


def avatar_directory_path(instance, filename):
    return f"user_{instance.id}/{filename}"


class MyUserManager(UserManager):
    def get_by_natural_key(self, username):
        return self.get(**{f"{self.model.USERNAME_FIELD}__iexact": username})


class User(AbstractUser):
    avatar = models.FileField(upload_to=avatar_directory_path, null=True, blank=True)
    date_of_create = models.DateTimeField(auto_now_add=True)
    last_connect = models.DateField(help_text="Последний вход", null=True, blank=True)
    phone = models.CharField(max_length=18, blank=True, null=True)

    objects = MyUserManager()

    class Meta:
        db_table = "user"

    def get_avatar(self):
        if not self.avatar.name:
            return f"{settings.MEDIA_URL}/avatar.jpg"
        return f"{settings.MEDIA_URL}/{self.avatar.name}"
