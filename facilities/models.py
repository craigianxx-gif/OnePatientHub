from django.db import models


class Facility(models.Model):

    FACILITY_TYPE_CHOICES = [

        ("Hospital", "Hospital"),

        ("Clinic", "Clinic"),

        ("Laboratory", "Laboratory"),

        ("Pharmacy", "Pharmacy"),

        ("Health Centre", "Health Centre"),

        ("Other", "Other"),

    ]

    facility_id = models.CharField(
        max_length=50,
        unique=True
    )

    facility_name = models.CharField(
        max_length=200
    )

    facility_type = models.CharField(
        max_length=50,
        choices=FACILITY_TYPE_CHOICES
    )

    country_code = models.CharField(
        max_length=2,
        default="ZW"
    )

    province = models.CharField(
        max_length=100
    )

    district = models.CharField(
        max_length=100
    )

    physical_address = models.TextField()

    phone_number = models.CharField(
        max_length=30,
        blank=True
    )

    email = models.EmailField(
        blank=True
    )

    fhir_organization_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        unique=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):

        return (
            f"{self.facility_id} - "
            f"{self.facility_name}"
        )