from django.contrib import admin
from .models import Referral

@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    
    # FIXED: Ensured "referring_facility" and "receiving_facility" are used instead of "facility"
    list_display = (
        "patient",
        "referring_facility",
        "receiving_facility",
        "referral_date",
        "status",
    )

    list_filter = (
        "status",
        "referral_date",
    )

    search_fields = (
        "patient__oph_id",
        "patient__national_id",
        "patient__first_name",
        "patient__last_name",
        "referring_facility__facility_name",
        "receiving_facility__facility_name",
    )