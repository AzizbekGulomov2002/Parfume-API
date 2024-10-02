import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from config import settings
from django.utils import timezone
import random


class CustomUserManager(BaseUserManager):
    def create_user(self, email, phone, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        if not phone:
            raise ValueError('The Phone field must be set')

        email = self.normalize_email(email)
        user = self.model(email=email, phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, phone, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    verification_code = models.IntegerField(null=True, blank=True)
    verification_code_time = models.DateTimeField(null=True, blank=True)
    new_password_temp = models.CharField(max_length=128, null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone']

    def __str__(self):
        return self.email

    def set_new_password(self, new_password):
        """Set a new password for the user."""
        self.set_password(new_password)
        self.new_password_temp = None  # Clear temporary password if applicable
        self.save()

    def generate_verification_code(self):
        """Generate and return a verification code."""
        self.verification_code = random.randint(10000, 99999)  # 5-digit code
        self.verification_code_time = timezone.now()  # Set current time
        self.save()
        return self.verification_code

    def is_verification_code_valid(self, code):
        """Check if the verification code is valid and hasn't expired."""
        if self.verification_code == code:
            time_difference = timezone.now() - self.verification_code_time
            # Assuming the code is valid for 10 minutes
            return time_difference.total_seconds() < 600
        return False



class UserImage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='images/')

    def __str__(self):
        return "User Images"