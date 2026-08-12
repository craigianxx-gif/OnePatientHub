from django.db import models
from patients.models import Patient
from facilities.models import Facility  # NEW: Import the Facility model


class Visit(models.Model):

    VISIT_TYPE_CHOICES = [
        ("Consultation", "Consultation"),
        ("Emergency", "Emergency"),
        ("Follow-up", "Follow-up"),
        ("Screening", "Screening"),
        ("Other", "Other"),
    ]

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="visits"
    )

    # CHANGED: Replaced facility_name text field with a Foreign Key
    facility = models.ForeignKey(
        Facility,
        on_delete=models.CASCADE,
        related_name="visits",
        null=True,  
        blank=True
    )

    visit_type = models.CharField(
        max_length=50,
        choices=VISIT_TYPE_CHOICES
    )

    reason = models.TextField()

    healthcare_provider = models.CharField(
        max_length=200
    )

    visit_date = models.DateField()

    notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        # CHANGED: Safely get the facility name for the string representation
        fac_name = self.facility.facility_name if self.facility else "Unknown Facility"
        return (
            f"{self.patient.oph_id} - "
            f"{fac_name} - "
            f"{self.visit_date}"
        )