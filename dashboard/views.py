from datetime import date

from django.shortcuts import render
from django.contrib.auth.models import User

from patients.models import (
    Patient,
    ExternalPatientIdentifier,
)

from facilities.models import Facility
from referrals.models import Referral
from audit.models import AuditLog
from accounts.models import AccountRequest


def dashboard_home(request):

    # =====================================
    # PATIENT STATISTICS
    # =====================================

    total_patients = Patient.objects.count()

    total_male = Patient.objects.filter(
        gender="Male"
    ).count()

    total_female = Patient.objects.filter(
        gender="Female"
    ).count()

    registered_today = Patient.objects.filter(
        created_at__date=date.today()
    ).count()

    # =====================================
    # FACILITY STATISTICS
    # =====================================

    total_facilities = Facility.objects.count()

    active_facilities = Facility.objects.filter(
        is_active=True
    ).count()

    hospitals = Facility.objects.filter(
        facility_type="Hospital"
    ).count()

    clinics = Facility.objects.filter(
        facility_type="Clinic"
    ).count()

    # =====================================
    # INTEROPERABILITY
    # =====================================

    external_identifiers = ExternalPatientIdentifier.objects.count()

    connected_facilities = Facility.objects.filter(
        is_active=True
    ).count()

    fhir_resources = Facility.objects.exclude(
        fhir_organization_id__isnull=True
    ).exclude(
        fhir_organization_id=""
    ).count()

    api_requests_today = 0

    # =====================================
    # HEALTH SYSTEM
    # =====================================

    total_referrals = Referral.objects.count()

    pending_referrals = Referral.objects.filter(
        status="Pending"
    ).count()

    patient_journeys = Referral.objects.values(
        "patient"
    ).distinct().count()

    # =====================================
    # SYSTEM
    # =====================================

    active_users = User.objects.filter(
        is_active=True
    ).count()

    pending_accounts = AccountRequest.objects.filter(
        status="pending"
    ).count()

    audit_events_today = AuditLog.objects.filter(
        timestamp__date=date.today()
    ).count()

    recent_audits = AuditLog.objects.all()[:5]

    context = {

        # Population
        "total_patients": total_patients,
        "total_male": total_male,
        "total_female": total_female,
        "registered_today": registered_today,

        # Facilities
        "total_facilities": total_facilities,
        "active_facilities": active_facilities,
        "hospitals": hospitals,
        "clinics": clinics,

        # Interoperability
        "external_identifiers": external_identifiers,
        "connected_facilities": connected_facilities,
        "fhir_resources": fhir_resources,
        "api_requests_today": api_requests_today,

        # Health System
        "total_referrals": total_referrals,
        "pending_referrals": pending_referrals,
        "patient_journeys": patient_journeys,

        # System
        "active_users": active_users,
        "pending_accounts": pending_accounts,
        "audit_events_today": audit_events_today,
        "recent_audits": recent_audits,

    }

    return render(
        request,
        "dashboard/dashboard.html",
        context
    )