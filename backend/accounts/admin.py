from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import FamilyGroup, User


@admin.register(FamilyGroup)
class FamilyGroupAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")
    search_fields = ("name",)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("id", "username", "role", "avatar", "family_group", "is_staff", "is_active")
    list_filter = ("role", "family_group", "is_staff", "is_active")
    fieldsets = UserAdmin.fieldsets + (
        ("额外信息", {"fields": ("role", "avatar", "family_group")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("额外信息", {"fields": ("role", "avatar", "family_group")}),
    )
    search_fields = ("username", "first_name", "last_name", "email")
