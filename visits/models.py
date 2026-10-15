from django.db import models
from patients.models import Patient
from facilities.models import Facility

class Visit(models.Model):
    VISIT_TYPE_CHOICES = [
        ("OPD", "Outpatient / Consultation"),
        ("Emergency", "Emergency"),
        ("Follow-up", "Follow-up"),
        ("Screening", "Screening"),
        ("ANC", "Antenatal Care"),
        ("DEL", "Facility Delivery"),
        ("PNC", "Postnatal Care"),
        ("Other", "Other"),
    ]

    TEST_TYPES = [
        ('NONE', 'No Test Administered'),
        ('HIV', 'HIV Screening'),
        ('TB', 'Tuberculosis Screening'),
        ('MALARIA', 'Malaria RDT/Microscopy'),
    ]

    TEST_RESULTS = [
        ('N/A', 'Not Applicable'),
        ('PENDING', 'Pending Results'),
        ('POSITIVE', 'Positive'),
        ('NEGATIVE', 'Negative'),
    ]

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="visits"
    )

    facility = models.ForeignKey(
        Facility,
        on_delete=models.CASCADE,
        related_name="visits",
        null=True,  
        blank=True
    )

    visit_type = models.CharField(
        max_length=50,
        choices=VISIT_TYPE_CHOICES,
        default="OPD"
    )

    test_type = models.CharField(
        max_length=15, 
        choices=TEST_TYPES, 
        default='NONE'
    )
    
    test_result = models.CharField(
        max_length=10, 
        choices=TEST_RESULTS, 
        default='N/A'
    )

    visit_date = models.DateField()

    blood_pressure = models.CharField(
        max_length=20, 
        blank=True, 
        null=True, 
        help_text="e.g., 120/80"
    )
    
    temperature = models.DecimalField(
        max_digits=4, 
        decimal_places=1, 
        blank=True, 
        null=True, 
        help_text="°C"
    )
    
    weight = models.DecimalField(
        max_digits=5, 
        decimal_places=1, 
        blank=True, 
        null=True, 
        help_text="kg"
    )

    reason = models.TextField(
        help_text="Chief complaint or reason for visit"
    )
    
    diagnosis = models.TextField(
        blank=True, 
        null=True
    )
    
    treatment_plan = models.TextField(
        blank=True, 
        null=True, 
        help_text="Includes prescriptions, procedures, and next steps"
    )

    notes = models.TextField(
        blank=True,
        help_text="General observations"
    )

    healthcare_provider = models.CharField(
        max_length=200
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        fac_name = self.facility.facility_name if self.facility else "Unknown Facility"
        return f"{self.patient.oph_id} - {fac_name} - {self.visit_date}"