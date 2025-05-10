# accounts/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user    = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    license = models.CharField("Licencia", max_length=64)

    def __str__(self):
        return f"Perfil de {self.user.username}"


