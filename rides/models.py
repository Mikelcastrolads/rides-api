from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.conf import settings


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required.")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("role", User.Role.ADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        RIDER = "rider", "Rider"
        DRIVER = "driver", "Driver"

    id_user = models.AutoField(primary_key=True)
    role = models.CharField(max_length=50, choices=Role.choices)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=50, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "role"]

    class Meta:
        db_table = "users"
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["role"]),
        ]

    def __str__(self):
        return self.email
    
class Ride(models.Model):
    class Status(models.TextChoices):
        EN_ROUTE = "en-route", "En Route"
        PICKUP = "pickup", "Pickup"
        DROPOFF = "dropoff", "Dropoff"

    id_ride = models.AutoField(primary_key=True)
    status = models.CharField(max_length=50, choices=Status.choices)

    id_rider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        db_column="id_rider",
        related_name="rides_as_rider",
        on_delete=models.CASCADE,
    )

    id_driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        db_column="id_driver",
        related_name="rides_as_driver",
        on_delete=models.CASCADE,
    )

    pickup_latitude = models.FloatField()
    pickup_longitude = models.FloatField()
    dropoff_latitude = models.FloatField()
    dropoff_longitude = models.FloatField()
    pickup_time = models.DateTimeField()

    class Meta:
        db_table = "rides"
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["pickup_time"]),
            models.Index(fields=["pickup_latitude", "pickup_longitude"]),
            models.Index(fields=["id_rider", "status"]),
        ]

    def __str__(self):
        return f"Ride #{self.id_ride} - {self.status}"


class RideEvent(models.Model):
    id_ride_event = models.AutoField(primary_key=True)

    id_ride = models.ForeignKey(
        Ride,
        db_column="id_ride",
        related_name="ride_events",
        on_delete=models.CASCADE,
    )

    description = models.CharField(max_length=255)
    created_at = models.DateTimeField()

    class Meta:
        db_table = "ride_events"
        indexes = [
            models.Index(fields=["id_ride", "created_at"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["description"]),
        ]

    def __str__(self):
        return f"RideEvent #{self.id_ride_event}"