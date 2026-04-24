from django.conf import settings
from django.db import models
from django.utils import timezone


class Lock(models.Model):
    name = models.CharField(max_length=150)
    device_id = models.CharField(max_length=100, unique=True)
    location = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    last_activity = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.device_id})"


class NFCCard(models.Model):
    uid = models.CharField(max_length=32, unique=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="nfc_cards",
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(default=True)
    comment = models.TextField(blank=True)
    deactivated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["uid"]

    def __str__(self):
        return self.uid


class AccessPermission(models.Model):
    card = models.ForeignKey(
        NFCCard,
        on_delete=models.CASCADE,
        related_name="permissions",
    )
    lock = models.ForeignKey(
        Lock,
        on_delete=models.CASCADE,
        related_name="permissions",
    )
    is_allowed = models.BooleanField(default=True)
    starts_at = models.DateTimeField(default=timezone.now)
    ends_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["lock__name", "card__uid"]
        constraints = [
            models.UniqueConstraint(
                fields=["card", "lock"],
                name="unique_card_lock_permission",
            )
        ]

    def __str__(self):
        return f"{self.card.uid} -> {self.lock.device_id}"


class AccessLog(models.Model):
    RESULT_ALLOWED = "allowed"
    RESULT_DENIED = "denied"
    RESULT_CHOICES = [
        (RESULT_ALLOWED, "Allowed"),
        (RESULT_DENIED, "Denied"),
    ]

    REASON_ACCESS_GRANTED = "access_granted"
    REASON_CARD_NOT_FOUND = "card_not_found"
    REASON_CARD_INACTIVE = "card_inactive"
    REASON_LOCK_NOT_FOUND = "lock_not_found"
    REASON_LOCK_INACTIVE = "lock_inactive"
    REASON_PERMISSION_NOT_FOUND = "permission_not_found"
    REASON_PERMISSION_EXPIRED = "permission_expired"
    REASON_SYSTEM_ERROR = "system_error"
    REASON_CHOICES = [
        (REASON_ACCESS_GRANTED, "Access granted"),
        (REASON_CARD_NOT_FOUND, "Card not found"),
        (REASON_CARD_INACTIVE, "Card inactive"),
        (REASON_LOCK_NOT_FOUND, "Lock not found"),
        (REASON_LOCK_INACTIVE, "Lock inactive"),
        (REASON_PERMISSION_NOT_FOUND, "Permission not found"),
        (REASON_PERMISSION_EXPIRED, "Permission expired"),
        (REASON_SYSTEM_ERROR, "System error"),
    ]

    uid = models.CharField(max_length=32)
    card = models.ForeignKey(
        NFCCard,
        on_delete=models.SET_NULL,
        related_name="access_logs",
        null=True,
        blank=True,
    )
    lock = models.ForeignKey(
        Lock,
        on_delete=models.SET_NULL,
        related_name="access_logs",
        null=True,
        blank=True,
    )
    card_found = models.BooleanField(default=False)
    result = models.CharField(max_length=10, choices=RESULT_CHOICES)
    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    raw_request = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.uid} - {self.result}"
