from django import forms
from .models import Referral

class ReferralForm(forms.ModelForm):

    class Meta:

        model = Referral

        fields = [
            "patient",
            "referring_facility",
            "receiving_facility",
            "reason",
            "clinical_notes",
        ]

        widgets = {
            
            # Adding Select dropdowns for the new ForeignKey relations
            "patient": forms.Select(
                attrs={
                    "class": "form-control"
                }
            ),
            
            "referring_facility": forms.Select(
                attrs={
                    "class": "form-control"
                }
            ),

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