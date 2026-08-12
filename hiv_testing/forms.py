from django import forms

from .models import HIVTest


class HIVTestForm(forms.ModelForm):

    class Meta:

        model = HIVTest

        fields = [
            "patient",
            "requesting_facility",
            "test_type",
            "sample_collection_date",
            "result",
            "result_submitted_date",
            "result_submitter",
            "status",
            "notes",
        ]

        widgets = {

            "sample_collection_date": forms.DateInput(
                attrs={
                    "type": "date"
                }
            ),

            "result_submitted_date": forms.DateInput(
                attrs={
                    "type": "date"
                }
            ),

            "notes": forms.Textarea(
                attrs={
                    "rows": 4
                }
            ),

        }