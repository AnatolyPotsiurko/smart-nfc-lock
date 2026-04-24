from django.contrib import admin

from .models import AccessLog, AccessPermission, Lock, NFCCard


@admin.register(Lock)
class LockAdmin(admin.ModelAdmin):
    list_display = ("name", "device_id", "location", "is_active", "last_activity")
    list_filter = ("is_active",)
    search_fields = ("name", "device_id", "location")


@admin.register(NFCCard)
class NFCCardAdmin(admin.ModelAdmin):
    list_display = ("uid", "owner", "is_active", "deactivated_at", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("uid", "owner__username", "owner__email")


@admin.register(AccessPermission)
class AccessPermissionAdmin(admin.ModelAdmin):
    list_display = ("card", "lock", "is_allowed", "is_active", "starts_at", "ends_at")
    list_filter = ("is_allowed", "is_active", "lock")
    search_fields = ("card__uid", "lock__name", "lock__device_id")


@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    list_display = ("uid", "card", "lock", "result", "reason", "created_at")
    list_filter = ("result", "reason", "lock", "created_at")
    search_fields = ("uid", "card__uid", "lock__name", "lock__device_id")
