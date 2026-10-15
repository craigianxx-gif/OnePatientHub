from datetime import date
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.db.models import Q

from patients.models import Patient, ExternalPatientIdentifier
from facilities.models import Facility
from referrals.models import Referral
from audit.models import AuditLog
from accounts.models import AccountRequest

def dashboard_home(request):
    
    is_global_view = request.user.is_superuser

    if is_global_view:
        # =====================================
        # MINISTRY OF HEALTH (GLOBAL VIEW)
        # =====================================
        
        total_patients = Patient.objects.count()
        total_male = Patient.objects.filter(gender="Male").count()
        total_female = Patient.objects.filter(gender="Female").count()
        registered_today = Patient.objects.filter(created_at__date=date.today()).count()

        total_facilities = Facility.objects.count()
        active_facilities = Facility.objects.filter(is_active=True).count()
        hospitals = Facility.objects.filter(facility_type="Hospital").count()
        clinics = Facility.objects.filter(facility_type="Clinic").count()

        total_referrals = Referral.objects.count()
        pending_referrals = Referral.objects.filter(status="Pending").count()
        patient_journeys = Referral.objects.values("patient").distinct().count()

        external_identifiers = ExternalPatientIdentifier.objects.count()
        fhir_resources = Facility.objects.exclude(fhir_organization_id__isnull=True).exclude(fhir_organization_id="").count()

        audit_events_today = AuditLog.objects.filter(timestamp__date=date.today()).count()
        recent_audits = AuditLog.objects.all().order_by('-timestamp')[:5]

        context = {
            "is_global_view": True,
            
            "total_patients": total_patients,
            "total_male": total_male,
            "total_female": total_female,
            "registered_today": registered_today,
            
            "total_facilities": total_facilities,
            "active_facilities": active_facilities,
            "hospitals": hospitals,
            "clinics": clinics,
            
            "total_referrals": total_referrals,
            "pending_referrals": pending_referrals,
            "patient_journeys": patient_journeys,
            
            "external_identifiers": external_identifiers,
            "fhir_resources": fhir_resources,
            "connected_facilities": active_facilities,
            "api_requests_today": 0,
            
            "audit_events_today": audit_events_today,
            "recent_audits": recent_audits,
        }

    else:
        # =====================================
        # FACILITY-ISOLATED (LOCAL VIEW)
        # =====================================
        active_facility_id = request.session.get('active_facility_id')
        
        if not active_facility_id:
            return redirect("login")
            
        active_facility = Facility.objects.filter(id=active_facility_id).first()

        facility_referrals = Referral.objects.filter(
            Q(referring_facility_id=active_facility_id) | 
            Q(receiving_facility_id=active_facility_id)
        )

        total_referrals = facility_referrals.count()
        pending_referrals = Referral.objects.filter(receiving_facility_id=active_facility_id, status="Pending").count()
        patient_journeys = facility_referrals.values("patient").distinct().count()

        facility_patient_ids = ExternalPatientIdentifier.objects.filter(
            facility_id=active_facility_id
        ).values_list('patient_id', flat=True)

        facility_patients = Patient.objects.filter(id__in=facility_patient_ids)

        total_patients = facility_patients.count()
        total_male = facility_patients.filter(gender="Male").count()
        total_female = facility_patients.filter(gender="Female").count()
        registered_today = facility_patients.filter(created_at__date=date.today()).count()

        external_identifiers = ExternalPatientIdentifier.objects.filter(facility_id=active_facility_id).count()

        audit_events_today = AuditLog.objects.filter(timestamp__date=date.today()).count()
        recent_audits = AuditLog.objects.all().order_by('-timestamp')[:5]

        context = {
            "is_global_view": False,
            "active_facility": active_facility,
            
            "total_patients": total_patients,
            "total_male": total_male,
            "total_female": total_female,
            "registered_today": registered_today,

            "total_referrals": total_referrals,
            "pending_referrals": pending_referrals,
            "patient_journeys": patient_journeys,
            
            "external_identifiers": external_identifiers,

            "audit_events_today": audit_events_today,
            "recent_audits": recent_audits,
        }

    return render(request, "dashboard/dashboard.html", context)