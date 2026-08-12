from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
import secrets
import hashlib

from patients.models import Patient
from facilities.models import Facility
from .models import ConnectedSystem, ApiKey, FhirTransaction

from .serializers import FHIRPatientSerializer, FHIROrganizationSerializer
from .pagination import FHIRBundlePagination
from .filters import PatientFilter


# ==========================================
# API DOCUMENTATION VIEWS
# ==========================================

@login_required
def api_endpoints_view(request):
    """
    Renders the API Endpoints documentation dashboard UI.
    """
    return render(request, 'api/api_endpoints.html')


@login_required
def fhir_resources_view(request):
    """
    Renders the FHIR Resources documentation and model schema dashboard UI.
    """
    return render(request, 'api/fhir_resources.html')


# ==========================================
# FHIR METADATA
# ==========================================

class FHIRMetadataView(APIView):
    """
    GET /api/fhir/metadata
    Returns the server's FHIR CapabilityStatement detailing supported capabilities.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        capability_statement = {
            "resourceType": "CapabilityStatement",
            "status": "active",
            "date": "2026-07-27",
            "kind": "instance",
            "software": {
                "name": "OnePatient Hub FHIR API",
                "version": "1.0.0"
            },
            "implementation": {
                "description": "OnePatient Hub National Interoperability Node"
            },
            "fhirVersion": "4.0.1",
            "format": ["json"],
            "rest": [
                {
                    "mode": "server",
                    "resource": [
                        {
                            "type": "Patient",
                            "interaction": [
                                {"code": "read"},
                                {"code": "update"},
                                {"code": "create"},
                                {"code": "search-type"}
                            ],
                            "searchParam": [
                                {"name": "family", "type": "string"},
                                {"name": "given", "type": "string"},
                                {"name": "gender", "type": "token"},
                                {"name": "identifier", "type": "token"}
                            ]
                        },
                        {
                            "type": "Organization",
                            "interaction": [
                                {"code": "read"},
                                {"code": "search-type"}
                            ]
                        }
                    ]
                }
            ]
        }
        return Response(capability_statement, status=status.HTTP_200_OK)


# ==========================================
# FHIR PATIENT ENDPOINTS
# ==========================================

class FHIRPatientList(generics.ListCreateAPIView):
    """
    GET /api/fhir/Patient
    POST /api/fhir/Patient
    """
    queryset = Patient.objects.prefetch_related('external_identifiers').all()
    serializer_class = FHIRPatientSerializer
    pagination_class = FHIRBundlePagination
    
    filter_backends = [DjangoFilterBackend]
    filterset_class = PatientFilter
    permission_classes = [IsAuthenticated]


class FHIRPatientDetail(generics.RetrieveUpdateAPIView):
    """
    GET /api/fhir/Patient/{oph_id}  - Read patient
    PUT /api/fhir/Patient/{oph_id}  - Update patient
    """
    queryset = Patient.objects.prefetch_related('external_identifiers').all()
    serializer_class = FHIRPatientSerializer
    lookup_field = 'oph_id'
    permission_classes = [IsAuthenticated]


# ==========================================
# FHIR ORGANIZATION ENDPOINTS
# ==========================================

class FHIROrganizationList(generics.ListAPIView):
    """
    GET /api/fhir/Organization
    """
    queryset = Facility.objects.all()
    serializer_class = FHIROrganizationSerializer
    pagination_class = FHIRBundlePagination
    permission_classes = [IsAuthenticated]


class FHIROrganizationDetail(generics.RetrieveAPIView):
    """
    GET /api/fhir/Organization/{facility_id}
    """
    queryset = Facility.objects.all()
    serializer_class = FHIROrganizationSerializer
    lookup_field = 'facility_id'
    permission_classes = [IsAuthenticated]


# ==========================================
# CONNECTED SYSTEMS INTEGRATION VIEWS
# ==========================================

@login_required
def connected_systems(request):
    """
    Renders the Connected Systems overview dashboard with live metrics.
    """
    systems = ConnectedSystem.objects.all()
    
    # Calculate metrics for the dashboard cards
    total_systems = systems.count()
    connected_systems_count = systems.filter(status="Connected").count()
    offline_systems = systems.filter(status__in=["Disconnected", "Maintenance"]).count()

    context = {
        "systems": systems,
        "total_systems": total_systems,
        "connected_systems_count": connected_systems_count,
        "offline_systems": offline_systems,
    }
    
    return render(request, 'api/connected_systems.html', context)


@login_required
def register_system(request):
    """
    Handles the registration of a new external connected system.
    """
    if request.method == "POST":
        system_name = request.POST.get("system_name")
        organization = request.POST.get("organization")
        system_type = request.POST.get("system_type")
        fhir_version = request.POST.get("fhir_version")
        base_url = request.POST.get("base_url")
        authentication = request.POST.get("authentication")
        status_val = request.POST.get("status")
        description = request.POST.get("description")

        # Save to database
        new_system = ConnectedSystem.objects.create(
            system_name=system_name,
            organization=organization,
            system_type=system_type,
            fhir_version=fhir_version,
            base_url=base_url,
            authentication=authentication,
            status=status_val,
            description=description
        )

        messages.success(request, f'Connected System "{new_system.system_name}" successfully registered.')
        return redirect('connected_systems')

    return render(request, 'api/register_system.html')


@login_required
def system_profile(request, pk):
    """
    Displays the details and credentials for a specific connected system.
    """
    system = get_object_or_404(ConnectedSystem, pk=pk)
    return render(request, 'api/system_profile.html', {"system": system})

@login_required
def edit_system(request, pk):
    """
    Handles updating an existing connected system's profile.
    """
    system = get_object_or_404(ConnectedSystem, pk=pk)

    if request.method == "POST":
        system.system_name = request.POST.get("system_name")
        system.organization = request.POST.get("organization")
        system.system_type = request.POST.get("system_type")
        system.fhir_version = request.POST.get("fhir_version")
        system.base_url = request.POST.get("base_url")
        system.authentication = request.POST.get("authentication")
        system.status = request.POST.get("status")
        system.description = request.POST.get("description")

        system.save()

        messages.success(request, f'Connected System "{system.system_name}" successfully updated.')
        return redirect('system_profile', pk=system.id)

    return render(request, 'api/edit_system.html', {"system": system})


# ==========================================
# API KEYS MANAGEMENT VIEWS
# ==========================================

@login_required
def api_keys_view(request):
    """
    Renders the API Keys management dashboard.
    Handles listing keys and generating new ones.
    """
    keys = ApiKey.objects.select_related('system').all()
    systems = ConnectedSystem.objects.all()
    
    generated_raw_key = None

    if request.method == "POST":
        action = request.POST.get("action")
        
        if action == "generate":
            system_id = request.POST.get("system_id")
            key_name = request.POST.get("name")
            expiry_days = int(request.POST.get("expiry_days", 90))
            
            system = get_object_or_404(ConnectedSystem, pk=system_id)
            
            # Generate secure token
            raw_token = f"oph_live_{secrets.token_urlsafe(32)}"
            prefix = raw_token[:10]
            key_hash = hashlib.sha256(raw_token.encode()).hexdigest()
            
            expires_at = timezone.now() + timedelta(days=expiry_days) if expiry_days > 0 else None
            
            ApiKey.objects.create(
                system=system,
                name=key_name,
                key_hash=key_hash,
                prefix=prefix,
                expires_at=expires_at
            )
            
            messages.success(request, f'API Key "{key_name}" generated successfully. Copy it now as it will not be shown again!')
            generated_raw_key = raw_token
            
        elif action == "revoke":
            key_id = request.POST.get("key_id")
            api_key = get_object_or_404(ApiKey, pk=key_id)
            api_key.is_active = False
            api_key.save()
            messages.warning(request, f'API Key "{api_key.name}" has been revoked.')
            return redirect('api_keys')

    context = {
        "keys": keys,
        "systems": systems,
        "generated_raw_key": generated_raw_key,
    }
    return render(request, 'api/api_keys.html', context)


# ==========================================
# FHIR TRANSACTIONS & PAYLOAD INSPECTION
# ==========================================

@login_required
def fhir_transactions_view(request):
    """
    Renders the FHIR Message and Payload Inspection transaction ledger.
    """
    transactions = FhirTransaction.objects.select_related('system').all()
    
    # Optional filtering by resource type if requested
    resource_filter = request.GET.get("resource")
    if resource_filter:
        transactions = transactions.filter(resource_type=resource_filter)

    context = {
        "transactions": transactions,
    }
    return render(request, 'api/fhir_transactions.html', context)