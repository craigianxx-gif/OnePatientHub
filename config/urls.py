from django.contrib import admin
from django.urls import path, include

from accounts import views as account_views

urlpatterns = [
    # Admin Panel
    path("admin/", admin.site.urls),
    
    # App Includes
    path("", include("accounts.urls")),
    path("patients/", include("patients.urls")),
    path("visits/", include("visits.urls")),
    path("referrals/", include("referrals.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("reports/", include("reports.urls")),
    path("facilities/", include("facilities.urls")),
    
    # FHIR Interoperability API Endpoints
    path("api/", include("api.urls")),
    
    path(
    "consent/",
    include("consent.urls")
),

    # Specific Account & Audit Views
    path("request-account/", account_views.request_account, name="request_account"),
    path("request-account/success/", account_views.request_account_success, name="request_account_success"),
    path("audit-logs/", account_views.audit_logs_view, name="audit_logs"),
]