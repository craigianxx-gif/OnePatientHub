from django import forms

from .models import Visit


class VisitForm(forms.ModelForm):

    class Meta:

        model = Visit

        # CHANGED: Replaced 'facility_name' with 'facility'
        fields = [
            "patient",
            "facility", 
            "visit_type",
            "reason",
            "healthcare_provider",
            "visit_date",
            "notes",
        ]

        widgets = {

            # CHANGED: Added a Select dropdown for the new facility relationship
            "facility": forms.Select(
                attrs={
                    "class": "form-control"
                }
            ),

            "patient": forms.Select(
                attrs={
                    "class": "form-control"
                }
            ),

            "visit_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control"
                }
            ),

            "reason": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": "form-control"
                }
            ),

            "notes": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": "form-control"
                }
            ),

        }