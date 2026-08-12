from django import forms

from .models import (
    Patient,
    ExternalPatientIdentifier
)


class PatientForm(forms.ModelForm):

    class Meta:

        model = Patient

        fields = [
            "national_id",
            "first_name",
            "last_name",
            "date_of_birth",
            "gender",
            "phone_number",
            "address"
        ]

        widgets = {

            "national_id": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter National ID"
                }
            ),

            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter First Name"
                }
            ),

            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Last Name"
                }
            ),

            "date_of_birth": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date"
                }
            ),

            "gender": forms.Select(
                attrs={
                    "class": "form-control"
                }
            ),

            "phone_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Phone Number"
                }
            ),

            "address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Address",
                    "rows": 3
                }
            ),

        }


class ExternalPatientIdentifierForm(
    forms.ModelForm
):

    class Meta:

        model = ExternalPatientIdentifier

        fields = [
            "system_name",
            "identifier",
            "facility",  # CHANGED: Replaced facility_name with facility
            "identifier_type"
        ]

        widgets = {

            "system_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder":
                    "e.g. Hospital EHR or LIMS"
                }
            ),

            "identifier": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder":
                    "e.g. HOSP-1001"
                }
            ),

            # CHANGED: Replaced TextInput with Select for the ForeignKey dropdown
            "facility": forms.Select(
                attrs={
                    "class": "form-control"
                }
            ),

            "identifier_type": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder":
                    "e.g. Facility Patient ID"
                }
            ),

        }