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

    PROVINCE_CHOICES = [
        ('BULAWAYO', 'Bulawayo Metropolitan'),
        ('HARARE', 'Harare Metropolitan'),
        ('MANICALAND', 'Manicaland'),
        ('MASH_CENTRAL', 'Mashonaland Central'),
        ('MASH_EAST', 'Mashonaland East'),
        ('MASH_WEST', 'Mashonaland West'),
        ('MASVINGO', 'Masvingo'),
        ('MAT_NORTH', 'Matabeleland North'),
        ('MAT_SOUTH', 'Matabeleland South'),
        ('MIDLANDS', 'Midlands'),
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
        max_length=50,
        choices=PROVINCE_CHOICES
    )

    district = models.CharField(
        max_length=100,
        help_text="e.g., Gwanda, Zvishavane, or Epworth"
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
    
    dhis2_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        unique=True,
        help_text="DHIS2 OrgUnit Code (e.g., OPH-HRE-001)"
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

    class Meta:
        verbose_name_plural = "Facilities"

    def __str__(self):
        return f"{self.facility_name} ({self.facility_id})"