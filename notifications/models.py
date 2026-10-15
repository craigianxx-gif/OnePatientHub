
from django.conf import settings
from django.db import models
from facilities.models import Facility
from referrals.models import Referral


class ReferralNotification(models.Model):
    referral = models.ForeignKey(
        Referral,
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    facility = models.ForeignKey(
        Facility,
        on_delete=models.CASCADE,
        related_name="referral_notifications"
    )
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Referral #{self.referral_id} - {self.facility.facility_name}"


class NotificationRead(models.Model):
    notification = models.ForeignKey(
        ReferralNotification,
        on_delete=models.CASCADE,
        related_name="read_records"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="referral_notification_reads"
    )
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["notification", "user"],
                name="unique_referral_notification_read"
            )
        ]

    def __str__(self):
        return f"Notification {self.notification_id} read by {self.user}"
