from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class CustomUserManager(BaseUserManager):
    """ Manager for CustomUser model """

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """ Custom user model using email instead of username """

    ROLE_CHOICES = [
        ('Student', 'Student'),
        ('Supervisor', 'Supervisor'),
        ('Dean Office', 'Dean Office'),
    ]

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True)
    is_profile_completed = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Required for Django Admin

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # No username required

    def save(self, *args, **kwargs):
        """ Automatically assign role based on email format """
        if not self.role:
            if '_' in self.email:
                self.role = 'Student'
            elif '.' in self.email:
                self.role = 'Supervisor'
            elif '-' in self.email:
                self.role = 'Dean Office'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.email} ({self.role})"
