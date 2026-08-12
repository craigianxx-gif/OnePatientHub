from django.db import models
from datetime import datetime
import random

# NEW: Import the Facility model
from facilities.models import Facility


def generate_luhn_checksum(base_digits):
    """
    Calculates the Luhn checksum digit for a string of digits.
    """
    total = 0
    for i, digit in enumerate(reversed(base_digits)):
        n = int(digit)
        if i % 2 == 0:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return str((10 - (total % 10)) % 10)


def generate_new_oph_id():
    """
    Generates a unique OPH-ID in the format: ZW-XXXX-XXXX-C
    """
    part1 = f"{random.randint(0, 9999):04d}"
    part2 = f"{random.randint(0, 9999):04d}"
    base_digits = f"{part1}{part2}"
    checksum = generate_luhn_checksum(base_digits)
    return f"ZW-{part1}-{part2}-{checksum}"


class Patient(models.Model):

    GENDER_CHOICES = [

        ("Male", "Male"),
        ("Female", "Female"),

    ]

    oph_id = models.CharField(
        max_length=20,
        unique=True,
        blank=True
    )

    national_id = models.CharField(
        max_length=20,
        unique=True
    )

    first_name = models.CharField(
        max_length=100
    )

    last_name = models.CharField(
        max_length=100
    )

    date_of_birth = models.DateField()

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES
    )

    phone_number = models.CharField(
        max_length=20
    )

    address = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def save(self, *args, **kwargs):
        if not self.oph_id:
            # Keep generating until we find a completely unique ID (preventing rare collisions)
            while True:
                candidate_id = generate_new_oph_id()
                if not Patient.objects.filter(oph_id=candidate_id).exists():
                    self.oph_id = candidate_id
                    break

        super().save(*args, **kwargs)

    def __str__(self):

        return (
            f"{self.oph_id} - "
            f"{self.first_name} "
            f"{self.last_name}"
        )


class ExternalPatientIdentifier(models.Model):

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="external_identifiers"
    )

    system_name = models.CharField(
        max_length=200
    )

    identifier = models.CharField(
        max_length=100
    )

    # CHANGED: Replaced facility_name text field with a Foreign Key
    facility = models.ForeignKey(
        Facility,
        on_delete=models.CASCADE,
        related_name="patient_identifiers",
        null=True,  
        blank=True
    )

    identifier_type = models.CharField(
        max_length=100,
        default="Facility Patient ID"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        constraints = [

            models.UniqueConstraint(
                fields=[
                    "system_name",
                    "identifier"
                ],
                name="unique_external_patient_identifier"
            )

        ]

    def __str__(self):
        
        # CHANGED: Updated string representation to use the new facility relation safely
        facility_name = self.facility.facility_name if self.facility else "Unknown Facility"

        return (
            f"{self.system_name}: "
            f"{self.identifier} - "
            f"{facility_name} "
            f"({self.patient.oph_id})"
        )