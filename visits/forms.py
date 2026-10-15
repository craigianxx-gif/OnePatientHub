from django import forms
from .models import Visit

class VisitForm(forms.ModelForm):

    class Meta:
        model = Visit

        # EXCLUDED: 'facility' and 'healthcare_provider' to enforce backend security
        fields = [
            "patient",
            "visit_date",
            "visit_type",
            "blood_pressure",
            "temperature",
            "weight",
            "reason",
            "diagnosis",
            "treatment_plan",
            "notes",
        ]

        widgets = {
            "patient": forms.Select(attrs={"class": "form-control"}),
            "visit_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "visit_type": forms.Select(attrs={"class": "form-control"}),
            "blood_pressure": forms.TextInput(attrs={"placeholder": "120/80", "class": "form-control"}),
            "temperature": forms.NumberInput(attrs={"placeholder": "37.0", "step": "0.1", "class": "form-control"}),
            "weight": forms.NumberInput(attrs={"placeholder": "75.5", "step": "0.1", "class": "form-control"}),
            
            "reason": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
            "diagnosis": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "treatment_plan": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "notes": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
        }