from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


class UserAdmin(BaseUserAdmin):
    ordering = ["id"]
    list_display = [
        "email", "first_name", "last_name", "role", "is_active", "is_staff", "auth0_id"
    ]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "phone")}),
        (_("Permissions"), {"fields": ("role", "is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Auth0 Info"), {"fields": ("auth0_id",)}),
        (_("Important dates"), {"fields": ("last_login", "created_at", "modified_at")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "phone", "first_name", "last_name", "password1", "password2", "role", "is_active", "is_staff"),
        }),
    )

    search_fields = ("email", "first_name", "last_name", "phone", "auth0_id")


admin.site.register(User, UserAdmin)
