from django.db import models

from patients.models import Patient

from django.contrib.auth.models import User


class PatientConsent(models.Model):

    CONSENT_TYPES = [

        ("GENERAL", "General Care"),

        ("REFERRAL", "Referral Sharing"),

        ("LABORATORY", "Laboratory Sharing"),

        ("RESEARCH", "Research"),

    ]


    STATUS_CHOICES = [

        ("GRANTED", "Granted"),

        ("REVOKED", "Revoked"),

        ("PENDING", "Pending"),

        ("EXPIRED", "Expired"),

    ]


    patient = models.ForeignKey(

        Patient,

        on_delete=models.CASCADE,

        related_name="consents"

    )


    consent_type = models.CharField(

        max_length=30,

        choices=CONSENT_TYPES

    )


    status = models.CharField(

        max_length=20,

        choices=STATUS_CHOICES,

        default="GRANTED"

    )


    granted_by = models.CharField(

        max_length=200

    )


    granted_date = models.DateField(

        auto_now_add=True

    )


    expiry_date = models.DateField(

        blank=True,

        null=True

    )


    emergency_override = models.BooleanField(

        default=False

    )


    notes = models.TextField(

        blank=True

    )


    created_by = models.ForeignKey(

        User,

        on_delete=models.SET_NULL,

        null=True,

        blank=True

    )


    created_at = models.DateTimeField(

        auto_now_add=True

    )


    updated_at = models.DateTimeField(

        auto_now=True

    )


    class Meta:

        ordering = [

            "-created_at"

        ]


        constraints = [

            models.UniqueConstraint(

                fields=[

                    "patient",

                    "consent_type"

                ],

                name="unique_patient_consent"

            )

        ]


    def __str__(self):

        return (

            f"{self.patient.oph_id} - "

            f"{self.get_consent_type_display()}"

        )