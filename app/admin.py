from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from app.models import Booking, CustomAuthenticationUser, Hotel, Review, Room


@admin.register(CustomAuthenticationUser)
class CustomAuthenticationUserAdmin(UserAdmin):
    model = CustomAuthenticationUser
    list_display = ("email", "full_name", "phone", "is_admin", "is_staff")
    list_filter = ("is_admin", "is_staff", "is_superuser", "is_active")
    ordering = ("email",)
    search_fields = ("email", "full_name", "phone")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Личные данные", {"fields": ("full_name", "phone")}),
        ("Права", {"fields": ("is_active", "is_staff", "is_superuser", "is_admin", "groups", "user_permissions")}),
        ("Даты", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "full_name", "phone", "password1", "password2", "is_staff", "is_admin"),
        }),
    )


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "address", "rating", "created_at")
    search_fields = ("title", "address", "owner__email")
    list_filter = ("created_at",)


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("hotel", "type", "price_on_one_day", "created_at")
    search_fields = ("hotel__title", "description")
    list_filter = ("type", "created_at")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("user", "room", "check_in", "check_out", "total_price", "created_at")
    search_fields = ("user__email", "room__hotel__title")
    list_filter = ("check_in", "check_out", "created_at")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("hotel", "user", "score", "created_at")
    search_fields = ("hotel__title", "user__email", "text")
    list_filter = ("score", "created_at")
