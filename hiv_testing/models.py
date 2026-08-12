from django.db import models
from patients.models import Patient


class HIVTest(models.Model):

    RESULT_CHOICES = [
        ("Pending", "Pending"),
        ("Positive", "Positive"),
        ("Negative", "Negative"),
        ("Indeterminate", "Indeterminate"),
    ]

    STATUS_CHOICES = [
        ("Requested", "Requested"),
        ("Sample Collected", "Sample Collected"),
        ("Result Submitted", "Result Submitted"),
    ]

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="hiv_tests"
    )

    requesting_facility = models.CharField(
        max_length=200
    )

    test_type = models.CharField(
    max_length=100,
    choices=[
        ("HIV", "HIV"),
        ("Malaria", "Malaria"),
        ("Tuberculosis", "Tuberculosis"),
        ("Maternal Care", "Maternal Care"),
    ],
    default="HIV"
    )

    sample_collection_date = models.DateField()

    result = models.CharField(
        max_length=20,
        choices=RESULT_CHOICES,
        default="Pending"
    )

    result_submitted_date = models.DateField(
        null=True,
        blank=True
    )

    result_submitter = models.CharField(
        max_length=200,
        blank=True
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="Requested"
    )

    notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return (
            f"{self.patient.oph_id} - "
            f"{self.test_type} - "
            f"{self.result}"
        )