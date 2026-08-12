from django import forms

from .models import Facility


class FacilityForm(forms.ModelForm):

    class Meta:

        model = Facility

        fields = [

            "facility_id",

            "facility_name",

            "facility_type",

            "country_code",

            "province",

            "district",

            "physical_address",

            "phone_number",

            "email",

            "fhir_organization_id",

            "is_active",

        ]

        widgets = {

            "facility_id": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. ZW-HOSP-0001",
                }
            ),

            "facility_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter facility name",
                }
            ),

            "facility_type": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "country_code": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "value": "ZW",
                    "maxlength": "2",
                }
            ),

            "province": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter province",
                }
            ),

            "district": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter district",
                }
            ),

            "physical_address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter physical address",
                    "rows": 3,
                }
            ),

            "phone_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter phone number",
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter email address",
                }
            ),

            "fhir_organization_id": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Optional FHIR Organization ID",
                }
            ),

            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),

        }