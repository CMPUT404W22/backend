import uuid

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class MyUserManager(UserManager):
    def _create_user(self, username, password, **extra_fields):
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password=None, **extra_fields):
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        return self._create_user(username, password, is_staff=True, is_superuser=True, **extra_fields)


class Author(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(_('username'), max_length=150, blank=False, null=False, unique=True)
    display_name = models.CharField(_('display name'), max_length=150, blank=False, null=False)
    github = models.CharField(_('github'), max_length=150, blank=False, null=False)
    image = models.CharField(_('profile image'), max_length=300, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(blank=False, null=False, default=True)
    is_staff = models.BooleanField(blank=False, null=False, default=False)
    is_superuser = models.BooleanField(blank=False, null=False, default=False)

    USERNAME_FIELD = "username"

    objects = MyUserManager()

    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        # created = not self.pk
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.display_name} {self.id}"