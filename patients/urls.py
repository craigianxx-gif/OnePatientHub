from django.urls import path
from . import views

urlpatterns = [

    # /patients/
    # Patient Directory
    path(
        "",
        views.patient_records,
        name="patient_directory"
    ),

    # /patients/register/
    # Register Patient
    path(
        "register/",
        views.register_patient,
        name="register_patient"
    ),

    # /patients/api/fhir/ingest/
    # FHIR Bundle POST Endpoint (Must be placed before <str:oph_id> routes)
    path(
        "api/fhir/ingest/",
        views.api_fhir_ingest_patients,
        name="api_fhir_ingest_patients"
    ),

    # /patients/<oph_id>/journey/
    # Patient Journey / Horizontal Tracking (Web View)
    path(
        "<str:oph_id>/journey/",
        views.patient_journey,
        name="patient_journey"
    ),

    # /patients/<oph_id>/journey/api/
    # Patient Journey / Horizontal Tracking (Interoperability API Endpoint)
    path(
        "<str:oph_id>/journey/api/",
        views.api_patient_journey,
        name="api_patient_journey"
    ),

    # /patients/<oph_id>/emergency-override/
    # Emergency Consent Override
    path(
        "<str:oph_id>/emergency-override/",
        views.trigger_emergency_override,
        name="trigger_emergency_override"
    ),

    # /patients/<oph_id>/emergency-override/end/
    # End Emergency Consent Override
    path(
        "<str:oph_id>/emergency-override/end/",
        views.end_emergency_override,
        name="end_emergency_override"
    ),

    # /patients/<oph_id>/
    # Patient Profile
    path(
        "<str:oph_id>/",
        views.patient_profile,
        name="patient_profile"
    ),

    # /patients/<oph_id>/edit/
    # Edit Patient
    path(
        "<str:oph_id>/edit/",
        views.edit_patient,
        name="edit_patient"
    ),

    # /patients/<oph_id>/delete/
    # Delete Patient
    path(
        "<str:oph_id>/delete/",
        views.delete_patient,
        name="delete_patient"
    ),

    # /patients/<oph_id>/add-identifier/
    # Add External Facility Identifier
    path(
        "<str:oph_id>/add-identifier/",
        views.add_external_identifier,
        name="add_external_identifier"
    ),
  
]