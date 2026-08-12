from django import forms

from .models import PatientConsent


class PatientConsentForm(forms.ModelForm):

    class Meta:

        model = PatientConsent

        fields = [

            "consent_type",

            "status",

            "granted_by",

            "expiry_date",

            "emergency_override",

            "notes",

        ]

        widgets = {

            "consent_type": forms.Select(

                attrs={

                    "class": "form-control"

                }

            ),

            "status": forms.Select(

                attrs={

                    "class": "form-control"

                }

            ),

            "granted_by": forms.TextInput(

                attrs={

                    "class": "form-control",

                    "placeholder": "Patient or Guardian"

                }

            ),

            "expiry_date": forms.DateInput(

                attrs={

                    "class": "form-control",

                    "type": "date"

                }

            ),

            "emergency_override": forms.CheckboxInput(

                attrs={

                    "class": "form-check-input"

                }

            ),

            "notes": forms.Textarea(

                attrs={

                    "class": "form-control",

                    "rows": 4,

                    "placeholder": "Additional notes"

                }

            ),

        }