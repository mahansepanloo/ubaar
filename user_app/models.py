from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("Phone number is required")
        user = self.model(phone_number=phone_number, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    phone_number = models.CharField(max_length=15, unique=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.phone_number


class FailedLoginAttempt(models.Model):
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    attempt_type = models.CharField(max_length=20, choices=[('login', 'Login'), ('otp', 'OTP')])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['phone_number', 'ip_address']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.phone_number or 'N/A'} - {self.attempt_type} attempt from {self.ip_address}"

    @classmethod
    def is_blocked_by_ip(cls, ip, scope, limit=3, block_duration=3600):
        cutoff = timezone.now() - timezone.timedelta(seconds=block_duration)
        attempts = cls.objects.filter(
            ip_address=ip, attempt_type=scope, created_at__gte=cutoff
        ).count()
        return attempts >= limit

    @classmethod
    def is_blocked_by_phone_and_ip(cls, phone, ip, scope, limit=3, block_duration=3600):
        cutoff = timezone.now() - timezone.timedelta(seconds=block_duration)
        attempts = cls.objects.filter(
            phone_number=phone, ip_address=ip, attempt_type=scope, created_at__gte=cutoff
        ).count()
        return attempts >= limit

    @classmethod
    def register_failure(cls, ip, phone=None, scope="otp"):
        cls.objects.create(ip_address=ip, phone_number=phone, attempt_type=scope)

    @classmethod
    def reset_failure(cls, ip, phone=None, scope="otp"):
        cls.objects.filter(ip_address=ip, phone_number=phone, attempt_type=scope).delete()