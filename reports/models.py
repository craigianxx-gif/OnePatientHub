from django.db import models
from django.contrib.auth.models import User
from facilities.models import Facility

class ReportSubmission(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Submitted to MoHCC/DHIS2'),
    ]

    period = models.CharField(max_length=6, help_text="Format: YYYYMM")
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, null=True, blank=True) # Null means National summary
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='DRAFT')
    payload_snapshot = models.JSONField(help_text="The exact JSON generated at time of submission")
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report {self.period} - {self.facility or 'National'}"