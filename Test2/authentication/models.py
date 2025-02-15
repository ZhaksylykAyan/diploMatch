from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now
import random
from django.conf import settings

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    ROLE_CHOICES = [
        ('student', 'Student'),
        ('professor', 'Professor'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

class OTPCode(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="otp")
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def generate_otp(self):
        """Генерируем 6-значный OTP-код и сохраняем его"""
        self.code = f"{random.randint(100000, 999999)}"
        self.created_at = now()
        self.save()
        return self.code

    def is_valid(self):
        """Проверяем, не истёк ли OTP-код (действителен 1 минуту)"""
        validity = (now() - self.created_at).seconds <= 60
        return validity