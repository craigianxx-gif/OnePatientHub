from django import forms
from .models import Referral

class ReferralForm(forms.ModelForm):

    class Meta:

        model = Referral

        fields = [
            "receiving_facility",
            "reason",
            "clinical_notes",
        ]

        widgets = {
            
            "receiving_facility": forms.Select(
                attrs={
                    "class": "form-control"
                }
            ),

            "reason": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": "form-control"
                }
            ),

            "clinical_notes": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": "form-control"
                }
            ),

        }

    def __init__(self, *args, **kwargs):
        # Extract active_facility_id before initializing the form
        active_facility_id = kwargs.pop('active_facility_id', None)
        super().__init__(*args, **kwargs)
        
        # Exclude the current facility from the receiving facility dropdown
        if active_facility_id:
            self.fields['receiving_facility'].queryset = self.fields['receiving_facility'].queryset.exclude(id=active_facility_id)