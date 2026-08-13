from django.db import models
from django.contrib.auth.models import User


class AuditLog(models.Model):

    ACTION_CHOICES = [

        ("LOGIN", "Login"),

        ("LOGOUT", "Logout"),

        ("CREATE", "Create"),

        ("VIEW", "View"),

        ("UPDATE", "Update"),

        ("DELETE", "Delete"),

        ("EXPORT", "Export"),

        ("OTHER", "Other"),
        
        ("EMERGENCY_OVERRIDE", "Emergency Override"),

    ]

    user = models.ForeignKey(

        User,

        on_delete=models.SET_NULL,

        null=True,

        blank=True,

        related_name="audit_logs"

    )

    action = models.CharField(

        max_length=20,

        choices=ACTION_CHOICES

    )

    module = models.CharField(

        max_length=100,

        default="System"

    )

    description = models.TextField()

    object_id = models.CharField(

        max_length=200,

        blank=True,

        null=True

    )

    ip_address = models.GenericIPAddressField(

        null=True,

        blank=True

    )

    timestamp = models.DateTimeField(

        auto_now_add=True

    )

    class Meta:

        ordering = [

            "-timestamp"

        ]

    def __str__(self):

        username = (

            self.user.username

            if self.user

            else "Unknown User"

        )

        return (

            f"{username} - "

            f"{self.action} - "

            f"{self.module}"

        )