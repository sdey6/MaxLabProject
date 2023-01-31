from random import randint

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class MyAccountManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError("user must have an email address")
        if not username:
            raise ValueError("user must have an username")

        user = self.model(
            email=self.normalize_email(email),  # convert to lower case character
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(
            email=self.normalize_email(email),  # convert to lower case character
            username=username,
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_active = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Account(AbstractBaseUser):
    email = models.EmailField(verbose_name="email", max_length=100, unique=True)
    username = models.CharField(max_length=100, unique=True)
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=True)
    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', ]

    objects = MyAccountManager()

    def __str__(self) -> str:
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True


class Room(models.Model):
    room_id = models.CharField(max_length=250, unique=True)
    room_name = models.CharField(max_length=250)
    username = models.CharField(max_length=250)
    email = models.EmailField(max_length=250)
    number_of_participants = models.IntegerField(default=2)
    duration = models.IntegerField(default=3)
    date_created = models.DateTimeField(verbose_name='date created', auto_now_add=True)
    is_audio_enabled = models.BooleanField(default=True)
    is_video_enabled = models.BooleanField(default=True)
    is_recording_audio_enabled = models.BooleanField(default=True)
    is_recording_video_enabled = models.BooleanField(default=True)
    is_transcription_enabled = models.BooleanField(default=False)
    status = models.CharField(max_length=100, default="NOT STARTED")

    def __str__(self) -> str:
        return f"{self.room_name} with {self.number_of_participants} participants " \
               f"for {self.duration} mins and {self.is_transcription_enabled} "
