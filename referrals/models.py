from django.db import models
from patients.models import Patient
from facilities.models import Facility  # NEW: Import the Facility model


class Referral(models.Model):

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Accepted", "Accepted"),
        ("Completed", "Completed"),
        ("Cancelled", "Cancelled"),
    ]

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="referrals"
    )

    # CHANGED: Replaced text field with ForeignKey to Facility
    referring_facility = models.ForeignKey(
        Facility,
        on_delete=models.CASCADE,
        related_name="referrals_made",
        null=True,
        blank=True
    )

    # CHANGED: Replaced text field with ForeignKey to Facility
    receiving_facility = models.ForeignKey(
        Facility,
        on_delete=models.CASCADE,
        related_name="referrals_received",
        null=True,
        blank=True
    )

    reason = models.TextField()

    clinical_notes = models.TextField(
        blank=True
    )

    referral_date = models.DateField(
        auto_now_add=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        # CHANGED: Safely get the facility names for the string representation
        ref_fac = self.referring_facility.facility_name if self.referring_facility else "Unknown"
        rec_fac = self.receiving_facility.facility_name if self.receiving_facility else "Unknown"
        
        return (
            f"{self.patient.oph_id} - "
            f"{ref_fac} to "
            f"{rec_fac}"
        )