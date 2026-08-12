from django.urls import path

from . import views


urlpatterns = [

    path(
        "",
        views.monthly_reports,
        name="monthly_reports"
    ),

    path(
        "export/<int:year>/<int:month>/",
        views.export_dhis2_json,
        name="export_dhis2_json"
    ),

    # --- NEW: Additional Export Endpoints ---

    path(
        "export/pdf/",
        views.export_report_pdf,
        name="export_report_pdf"
    ),

    path(
        "export/csv/",
        views.export_report_csv,
        name="export_report_csv"
    ),

    path(
        "export/fhir/",
        views.export_fhir_bundle,
        name="export_fhir_bundle"
    ),

]