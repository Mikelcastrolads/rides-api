from django.contrib import admin
from .models import User, Ride, RideEvent


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id_user",
        "email",
        "role",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
    )
    search_fields = ("email", "first_name", "last_name")
    list_filter = ("role", "is_active", "is_staff")


@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    list_display = (
        "id_ride",
        "status",
        "id_rider",
        "id_driver",
        "pickup_time",
    )
    search_fields = ("id_rider__email", "id_driver__email")
    list_filter = ("status", "pickup_time")


@admin.register(RideEvent)
class RideEventAdmin(admin.ModelAdmin):
    list_display = (
        "id_ride_event",
        "id_ride",
        "description",
        "created_at",
    )
    search_fields = ("description",)
    list_filter = ("created_at",)