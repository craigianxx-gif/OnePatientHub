from django import forms
from .models import AccountRequest

class AccountRequestForm(forms.ModelForm):
    class Meta:
        model = AccountRequest
        # We changed 'work_email' to 'email', and added 'staff_id'
        fields = ['full_name', 'email', 'phone_number', 'staff_id', 'requested_role']