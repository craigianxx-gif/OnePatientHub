from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    # API Documentation UI Views
    path('endpoints/', views.api_endpoints_view, name='api_endpoints_ui'),
    path('resources/', views.fhir_resources_view, name='fhir_resources_ui'),

    # Metadata Endpoint
    path('fhir/metadata', views.FHIRMetadataView.as_view(), name='fhir_metadata'),

    # Patient Endpoints
    path('fhir/Patient', views.FHIRPatientList.as_view(), name='fhir_patient_list'),
    path('fhir/Patient/<str:oph_id>', views.FHIRPatientDetail.as_view(), name='fhir_patient_detail'),

    # Organization (Facility) Endpoints
    path('fhir/Organization', views.FHIROrganizationList.as_view(), name='fhir_organization_list'),
    path('fhir/Organization/<str:facility_id>', views.FHIROrganizationDetail.as_view(), name='fhir_organization_detail'),
    
    # Connected Systems Endpoints
    path("connected-systems/", views.connected_systems, name="connected_systems"),
    path("connected-systems/register/", views.register_system, name="register_system"),
    path("connected-systems/<int:pk>/", views.system_profile, name="system_profile"),
    path("connected-systems/<int:pk>/edit/", views.edit_system, name="edit_system"),
    
    # API Keys Management
    path("api-keys/", views.api_keys_view, name="api_keys"),
    
    # FHIR Transactions & Payload Inspection
    path("fhir/transactions/", views.fhir_transactions_view, name="fhir_transactions"),
]

# Enables URLs like /fhir/Patient.json natively
urlpatterns = format_suffix_patterns(urlpatterns)