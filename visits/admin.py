from django.contrib import admin
from .models import Visit

@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    
    # CHANGED: "facility_name" is now "facility"
    list_display = (
        "patient",
        "facility", 
        "visit_type",
        "visit_date",
    )
    
    list_filter = (
        "visit_type",
        "visit_date",
    )
    
    # CHANGED: "facility_name" is now "facility__facility_name"
    search_fields = (
        "patient__oph_id",
        "patient__first_name",
        "patient__last_name",
        "facility__facility_name",
        "healthcare_provider",
    )