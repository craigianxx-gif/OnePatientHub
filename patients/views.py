# views.py
import random
import datetime  
import json

from django.utils import timezone
from datetime import timedelta

from audit.models import AuditLog

from django.shortcuts import (
    render,
    get_object_or_404,
    redirect
)

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.contrib import messages
from django.http import JsonResponse

from audit.utils import create_audit_log
from consent.models import PatientConsent
from facilities.models import Facility

from .forms import (
    PatientForm,
    ExternalPatientIdentifierForm
)

from .models import Patient, ExternalPatientIdentifier


# OPH-ID Generation

def calculate_luhn_checksum(number_str):

    total = 0

    reverse_digits = [
        int(x)
        for x in reversed(number_str)
    ]

    for i, digit in enumerate(reverse_digits):

        if i % 2 == 0:

            digit *= 2

            if digit > 9:
                digit -= 9

        total += digit

    return (
        10 - (total % 10)
    ) % 10


def generate_oph_id(country_code):
    """
    Generates an OPH-ID in the format: ZW-4512-0876-3
    """
    while True:

        base_number = str(
            random.randint(
                10000000,
                99999999
            )
        )

        checksum = calculate_luhn_checksum(
            base_number
        )

        part1 = base_number[:4]
        part2 = base_number[4:]

        oph_id = (
            f"{country_code}-"
            f"{part1}-"
            f"{part2}-"
            f"{checksum}"
        )

        if not Patient.objects.filter(
            oph_id=oph_id
        ).exists():

            return oph_id


# Register Patient

@login_required
def register_patient(request):
    
    active_facility_id = request.session.get('active_facility_id')
    
    if not active_facility_id:
        messages.error(request, "Session expired. Please select a facility to continue.")
        return redirect("login")

    if request.method == "POST":

        form = PatientForm(
            request.POST
        )

        if form.is_valid():

            patient = form.save(
                commit=False
            )

            try:

                country_code = (
                    request.user.profile.country_code
                    or "ZW"
                )

            except AttributeError:

                country_code = "ZW"

            patient.oph_id = generate_oph_id(
                country_code
            )

            patient.save()

            # Link patient to the facility they were registered at
            facility = Facility.objects.get(id=active_facility_id)
            ExternalPatientIdentifier.objects.create(
                patient=patient,
                system_name="OnePatient Hub Web Client",
                identifier=f"{facility.facility_name[:4].upper()}-{patient.oph_id}",
                facility=facility,
                identifier_type="Initial Registration"
            )

            create_audit_log(
                request=request,
                action="CREATE",
                module="Patients",
                description=(
                    f"Registered patient "
                    f"{patient.oph_id} at "
                    f"{facility.facility_name}"
                ),
                object_id=patient.oph_id
            )

            messages.success(request, f"Patient {patient.first_name} {patient.last_name} successfully registered!")

            return redirect(
                "patient_profile",
                oph_id=patient.oph_id
            )

    else:

        form = PatientForm()

    return render(
        request,
        "patients/register_patient.html",
        {
            "form": form
        }
    )


# Patient Directory

@login_required
def patient_records(request):

    active_facility_id = request.session.get('active_facility_id')
    
    if not active_facility_id:
        messages.error(request, "Session expired. Please log in again.")
        return redirect("login")

    query = request.GET.get(
        "q",
        ""
    )

    if query:
        # Global search: query the central registry
        patients = Patient.objects.filter(
            Q(oph_id__icontains=query) |
            Q(national_id__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        ).distinct().order_by("-created_at")
        
    else:
        # Local list: only show patients connected to this facility
        patients = Patient.objects.filter(
            Q(visits__facility_id=active_facility_id) |
            Q(external_identifiers__facility_id=active_facility_id) |
            Q(referrals__referring_facility_id=active_facility_id) |
            Q(referrals__receiving_facility_id=active_facility_id)
        ).distinct().order_by("-created_at")

    return render(

        request,

        "patients/patient_records.html",

        {
            "patients": patients,
            "query": query,
            "is_global_search": bool(query)
        }

    )


# Patient Profile

@login_required
def patient_profile(request, oph_id):

    patient = get_object_or_404(
        Patient,
        oph_id=oph_id
    )
    
    consent = PatientConsent.objects.filter(
        patient=patient
    ).first()

    visits = (
        patient.visits
        .select_related(
            "facility"
        )
        .all()
        .order_by(
            "-visit_date"
        )
    )

    referrals = (
        patient.referrals
        .select_related(
            "referring_facility",
            "receiving_facility"
        )
        .all()
        .order_by(
            "-created_at"
        )
    )

    external_identifiers = (
        patient.external_identifiers
        .select_related(
            "facility"
        )
        .all()
        .order_by(
            "-created_at"
        )
    )

    timeline_events = []

    timeline_events.append({
        "event_type": "Patient Registered",
        "event_category": "registration",
        "date": patient.created_at,
        "facility": "OnePatient Hub",
        "description": "Patient identity created in the OnePatient Hub identity registry.",
        "status": "Completed",
        "icon": "user",
        "actor": "System Registry",
        "sequence": 1
    })

    for visit in visits:
        facility_name = visit.facility.facility_name if visit.facility else "Unknown Facility"

        timeline_events.append({
            "event_type": "Healthcare Visit",
            "event_category": "visit",
            "date": getattr(visit, 'created_at', visit.visit_date),
            "facility": facility_name,
            "description": f"{visit.visit_type}: {visit.reason}",
            "notes": visit.notes,
            "status": "Completed",
            "icon": "calendar",
            "actor": visit.healthcare_provider or "Clinical Staff",
            "sequence": 2
        })

    for referral in referrals:
        referring_facility = referral.referring_facility.facility_name if referral.referring_facility else "Unknown Facility"
        receiving_facility = referral.receiving_facility.facility_name if referral.receiving_facility else "Unknown Facility"

        timeline_events.append({
            "event_type": "Patient Referral",
            "event_category": "referral",
            "date": getattr(referral, 'created_at', referral.referral_date),
            "facility": f"{referring_facility} → {receiving_facility}",
            "description": referral.reason,
            "clinical_notes": referral.clinical_notes,
            "status": referral.status,
            "icon": "arrow",
            "actor": "Referring Facility Staff",
            "sequence": 3
        })

    for identifier in external_identifiers:
        facility_name = identifier.facility.facility_name if identifier.facility else getattr(identifier, "facility_name", "External System")

        timeline_events.append({
            "event_type": "External Identifier Linked",
            "event_category": "identity",
            "date": identifier.created_at,
            "facility": facility_name,
            "description": f"System: {identifier.system_name} | Identifier: {identifier.identifier}",
            "status": "Linked",
            "icon": "link",
            "actor": "System Registry",
            "sequence": 0
        })

    # NEW ADVANCED SORTING: Group by Calendar Day, then Order by Clinical Sequence
    for event in timeline_events:
        if not isinstance(event["date"], datetime.datetime):
            dt = timezone.make_aware(datetime.datetime.combine(event["date"], datetime.time.min))
        else:
            dt = event["date"]
            
        event["sort_date"] = dt
        event["bucket_date"] = dt.date()

    timeline_events.sort(
        key=lambda x: (x["bucket_date"], x.get("sequence", 0), x["sort_date"]), 
        reverse=True
    )

    create_audit_log(
        request=request,
        action="VIEW",
        module="Patients",
        description=(
            f"Viewed patient profile "
            f"{patient.oph_id}"
        ),
        object_id=patient.oph_id
    )

    return render(
        request,
        "patients/patient_profile.html",
        {
            "patient": patient,
            "visits": visits,
            "referrals": referrals,
            "external_identifiers": external_identifiers,
            "timeline_events": timeline_events,
            "consent": consent
        }
    )


# Add External Identifier

@login_required
def add_external_identifier(request, oph_id):

    patient = get_object_or_404(
        Patient,
        oph_id=oph_id
    )

    active_facility_id = request.session.get('active_facility_id')

    if request.method == "POST":

        form = (
            ExternalPatientIdentifierForm(
                request.POST
            )
        )

        if form.is_valid():

            external_identifier = (
                form.save(
                    commit=False
                )
            )
            external_identifier.patient = patient
            external_identifier.facility_id = active_facility_id
            external_identifier.save()

            create_audit_log(
                request=request,
                action="CREATE",
                module="Patient Identity",
                description=(
                    f"Added external identifier "
                    f"{external_identifier.identifier} "
                    f"from "
                    f"{external_identifier.system_name} "
                    f"to patient "
                    f"{patient.oph_id}"
                ),
                object_id=patient.oph_id
            )

            return redirect(
                "patient_profile",
                oph_id=patient.oph_id
            )
    else:
        form = ExternalPatientIdentifierForm()

    return render(
        request,
        "patients/add_external_identifier.html",
        {
            "patient": patient,
            "form": form
        }
    )


# Edit Patient

@login_required
def edit_patient(request, oph_id):

    patient = get_object_or_404(
        Patient,
        oph_id=oph_id
    )

    if request.method == "POST":

        form = PatientForm(
            request.POST,
            instance=patient
        )

        if form.is_valid():

            form.save()

            create_audit_log(
                request=request,
                action="UPDATE",
                module="Patients",
                description=(
                    f"Updated patient "
                    f"{patient.oph_id}"
                ),
                object_id=patient.oph_id
            )

            return redirect(
                "patient_profile",
                oph_id=patient.oph_id
            )
    else:
        form = PatientForm(instance=patient)

    return render(
        request,
        "patients/edit_patient.html",
        {
            "form": form,
            "patient": patient
        }
    )


# Delete Patient

@login_required
def delete_patient(request, oph_id):

    patient = get_object_or_404(
        Patient,
        oph_id=oph_id
    )

    if request.method == "POST":

        patient_oph_id = patient.oph_id

        create_audit_log(
            request=request,
            action="DELETE",
            module="Patients",
            description=(
                f"Deleted patient "
                f"{patient_oph_id}"
            ),
            object_id=patient_oph_id
        )

        patient.delete()
        return redirect("patient_directory")

    return render(
        request,
        "patients/delete_patient.html",
        {
            "patient": patient
        }
    )


# Patient Journey / Horizontal Tracking View

@login_required
def patient_journey(request, oph_id):
    patient = get_object_or_404(Patient, oph_id=oph_id)
    consent = PatientConsent.objects.filter(patient=patient).first()

    is_emergency_override = False
    override_data = request.session.get(f"emergency_override_{oph_id}")

    override_expires_at = None
    override_user = request.user.get_full_name() or request.user.username
    override_reason = "Urgent clinical care protocol"

    if override_data and not isinstance(override_data, bool):
        try:
            trigger_time = datetime.datetime.fromtimestamp(
                float(override_data), 
                tz=datetime.timezone.utc
            )
            if timezone.now() - trigger_time <= timedelta(minutes=60):
                is_emergency_override = True
                override_expires_at = (trigger_time + timedelta(minutes=60)).isoformat()
                
                log = AuditLog.objects.filter(object_id=patient.oph_id, action="EMERGENCY_OVERRIDE").order_by('-timestamp').first()
                if log:
                    override_user = log.user.get_full_name() or log.user.username
                    if "Reason:" in log.description:
                        override_reason = log.description.split("Reason: ")[-1]
                        
            else:
                del request.session[f"emergency_override_{oph_id}"]
                request.session.modified = True
                messages.error(request, "🔒 Emergency override period (60 min) has expired. Access revoked.")
        except (ValueError, TypeError):
            del request.session[f"emergency_override_{oph_id}"]
            request.session.modified = True
    elif override_data:
        del request.session[f"emergency_override_{oph_id}"]
        request.session.modified = True

    if (not consent or consent.status not in ["Granted", "Active", "Yes", "GRANTED"]) and not is_emergency_override:
        messages.warning(request, "Access restricted: Patient has not granted cross-facility data sharing consent.")
        return redirect("patient_profile", oph_id=patient.oph_id)

    visits = patient.visits.select_related("facility").all().order_by("-visit_date")
    referrals = patient.referrals.select_related("referring_facility", "receiving_facility").all().order_by("-referral_date")
    external_identifiers = patient.external_identifiers.select_related("facility").all().order_by("-created_at")

    timeline_events = []

    timeline_events.append({
        "date": patient.created_at,
        "facility": "OnePatient Hub Identity Registry",
        "event_type": "Registration",
        "event_category": "registration",
        "description": "Patient identity registered and master OPH-ID generated.",
        "status": "Completed",
        "source": "Patient Registry",
        "actor": "System Auto-Registration",
        "sequence": 1
    })

    for visit in visits:
        facility_name = visit.facility.facility_name if visit.facility else "Unknown Facility"
        timeline_events.append({
            "date": getattr(visit, 'created_at', visit.visit_date),
            "facility": facility_name,
            "event_type": f"Visit ({visit.visit_type})",
            "event_category": "visit",
            "description": f"Clinical consultation: {visit.reason}.",
            "status": "Completed",
            "source": f"Visit #{visit.id}",
            "actor": visit.healthcare_provider or "Clinical Staff",
            "sequence": 2
        })

    for referral in referrals:
        ref_fac = referral.referring_facility.facility_name if referral.referring_facility else "Unknown Facility"
        rec_fac = referral.receiving_facility.facility_name if referral.receiving_facility else "Unknown Facility"

        timeline_events.append({
            "date": getattr(referral, 'created_at', referral.referral_date),
            "facility": ref_fac,
            "event_type": "Referral Created",
            "event_category": "referral",
            "description": f"Outbound referral created for transfer to {rec_fac}. Clinical reason: {referral.reason}",
            "status": referral.status,
            "source": f"Referral #{referral.id}",
            "actor": "Referring Staff",
            "sequence": 3
        })

        if referral.status in ["Accepted", "Completed"]:
            timeline_events.append({
                "date": getattr(referral, 'updated_at', referral.referral_date),
                "facility": rec_fac,
                "event_type": "Referral Received & Accepted",
                "event_category": "referral",
                "description": f"Inbound referral accepted from {ref_fac}. Transfer of care confirmed.",
                "status": "Accepted",
                "source": f"Referral #{referral.id}",
                "actor": "Receiving Staff",
                "sequence": 4
            })

        if referral.status == "Completed":
            timeline_events.append({
                "date": getattr(referral, 'updated_at', referral.created_at),
                "facility": rec_fac,
                "event_type": "Referral Completed",
                "event_category": "referral",
                "description": f"Referred clinical episode completed at {rec_fac}.",
                "status": "Completed",
                "source": f"Referral #{referral.id}",
                "actor": "Receiving Staff",
                "sequence": 5
            })

    # Advanced Sorting logic
    for event in timeline_events:
        if not isinstance(event["date"], datetime.datetime):
            dt = timezone.make_aware(datetime.datetime.combine(event["date"], datetime.time.min))
        else:
            dt = event["date"]
            
        event["sort_date"] = dt
        event["bucket_date"] = dt.date()

    timeline_events.sort(
        key=lambda x: (x["bucket_date"], x.get("sequence", 0), x["sort_date"]), 
        reverse=True
    )

    last_recorded_facility = "No clinical records"
    last_recorded_activity = "None"
    last_recorded_date = None

    for event in timeline_events:
        if event["event_category"] in ["visit", "referral"]:
            last_recorded_facility = event["facility"]
            last_recorded_activity = event["event_type"]
            last_recorded_date = event["sort_date"]
            break

    chronological_events = sorted(timeline_events, key=lambda x: (x["bucket_date"], x.get("sequence", 0), x["sort_date"]))
    movement_path = []
    for event in chronological_events:
        if event["event_category"] in ["visit", "referral"]:
            fac = event["facility"]
            if not movement_path or movement_path[-1] != fac:
                movement_path.append(fac)

    selected_facility = request.GET.get("facility", "").strip()
    selected_event_type = request.GET.get("event_type", "").strip()
    date_from = request.GET.get("date_from", "").strip()
    date_to = request.GET.get("date_to", "").strip()

    filtered_events = timeline_events

    if selected_facility:
        filtered_events = [e for e in filtered_events if e["facility"] == selected_facility]

    if selected_event_type:
        filtered_events = [e for e in filtered_events if selected_event_type.lower() in e["event_category"].lower()]

    if date_from:
        try:
            df = datetime.datetime.strptime(date_from, "%Y-%m-%d").date()
            filtered_events = [e for e in filtered_events if e["bucket_date"] >= df]
        except ValueError:
            pass

    if date_to:
        try:
            dt = datetime.datetime.strptime(date_to, "%Y-%m-%d").date()
            filtered_events = [e for e in filtered_events if e["bucket_date"] <= dt]
        except ValueError:
            pass

    all_facilities = Facility.objects.filter(is_active=True).order_by("facility_name")
    access_mode = "Emergency Override" if is_emergency_override else "Consent Granted"
    user_facility_name = getattr(request.user.profile, 'facility', None) or "Central Registry Access"

    create_audit_log(
        request=request,
        action="VIEW",
        module="Patient Journey",
        description=(
            f"Horizontal Care Journey accessed for {patient.oph_id}. "
            f"User: {request.user.username} | Facility: {user_facility_name} | Mode: {access_mode}"
        ),
        object_id=patient.oph_id
    )

    return render(
        request,
        "patients/patient_journey.html",
        {
            "patient": patient,
            "timeline_events": filtered_events,
            "last_recorded_facility": last_recorded_facility,
            "last_recorded_activity": last_recorded_activity,
            "last_recorded_date": last_recorded_date,
            "movement_path": movement_path,
            "external_identifiers": external_identifiers,
            "all_facilities": all_facilities,
            "selected_facility": selected_facility,
            "selected_event_type": selected_event_type,
            "date_from": date_from,
            "date_to": date_to,
            "is_emergency_override": is_emergency_override,
            "override_expires_at": override_expires_at,
            "override_user": override_user,
            "override_reason": override_reason,
            "total_events_count": len(timeline_events),
            "filtered_events_count": len(filtered_events)
        }
    )


# API: Patient Journey JSON Endpoint (Interoperability)

def api_patient_journey(request, oph_id):
    patient = get_object_or_404(Patient, oph_id=oph_id)
    consent = PatientConsent.objects.filter(patient=patient).first()

    if not consent or consent.status not in ["Granted", "Active", "Yes", "GRANTED"]:
        return JsonResponse(
            {"error": "Access restricted: Consent not granted for cross-facility access."}, 
            status=403
        )

    visits = patient.visits.select_related("facility").all().order_by("visit_date")
    referrals = patient.referrals.select_related("referring_facility", "receiving_facility").all().order_by("referral_date")

    journey_items = []

    journey_items.append({
        "date": patient.created_at.strftime("%Y-%m-%d"),
        "facility": "OnePatient Hub Identity Registry",
        "event": "Registration",
        "description": "Patient identity registered.",
        "status": "Completed"
    })

    for v in visits:
        journey_items.append({
            "date": v.visit_date.strftime("%Y-%m-%d"),
            "facility": v.facility.facility_name if v.facility else "Unknown",
            "event": f"Visit ({v.visit_type})",
            "description": v.reason,
            "status": "Completed"
        })

    for r in referrals:
        journey_items.append({
            "date": r.referral_date.strftime("%Y-%m-%d"),
            "facility": r.referring_facility.facility_name if r.referring_facility else "Unknown",
            "event": "Referral",
            "description": f"Referred to {r.receiving_facility.facility_name if r.receiving_facility else 'Unknown'}",
            "status": r.status
        })

    journey_items.sort(key=lambda x: x["date"], reverse=True)

    ext_ids = [
        {
            "facility": i.facility.facility_name if i.facility else i.system_name,
            "system_name": i.system_name,
            "identifier": i.identifier
        }
        for i in patient.external_identifiers.select_related("facility").all()
    ]

    create_audit_log(
        request=request,
        action="API_EXPORT",
        module="Interoperability API",
        description=f"Exported JSON Patient Journey for {patient.oph_id} to external consumer.",
        object_id=patient.oph_id
    )

    return JsonResponse({
        "oph_id": patient.oph_id,
        "patient_name": f"{patient.first_name} {patient.last_name}",
        "external_identifiers": ext_ids,
        "journey": journey_items
    })


# Trigger Emergency Override

@login_required
def trigger_emergency_override(
    request,
    oph_id
):

    patient = get_object_or_404(
        Patient,
        oph_id=oph_id
    )

    if request.method == "POST":

        reason = request.POST.get(
            "override_reason",
            ""
        ).strip()
        
        if not reason:
            messages.error(
                request,
                "A valid clinical justification reason is required to trigger an emergency override."
            )
            return render(
                request,
                "patients/emergency_override.html",
                {"patient": patient}
            )

        request.session[f"emergency_override_{oph_id}"] = timezone.now().timestamp()
        request.session.modified = True
        
        try:
            create_audit_log(
                request=request,
                action="EMERGENCY_OVERRIDE",
                module="Consent Management",
                description=(
                    f"EMERGENCY OVERRIDE triggered for patient {patient.oph_id}. "
                    f"Reason: {reason}"
                ),
                object_id=patient.oph_id
            )
        except Exception as e:
            print(f"\n❌ AUDIT LOG ERROR DURING OVERRIDE: {str(e)}\n")

        messages.warning(
            request,
            "⚠️ Emergency override active. Access granted under urgent care protocol."
        )

        return redirect(
            "patient_journey",
            oph_id=patient.oph_id
        )
        
    return render(
        request,
        "patients/emergency_override.html",
        {
            "patient": patient
        }
    )

# End Emergency Override

@login_required
def end_emergency_override(request, oph_id):
    patient = get_object_or_404(Patient, oph_id=oph_id)
    session_key = f"emergency_override_{oph_id}"

    if session_key in request.session:
        del request.session[session_key]
        request.session.modified = True

        create_audit_log(
            request=request,
            action="UPDATE", 
            module="Consent Management",
            description=f"EMERGENCY OVERRIDE manually revoked for patient {patient.oph_id}.",
            object_id=patient.oph_id
        )

        messages.success(request, "Emergency override successfully revoked. Standard access controls restored.")

    return redirect("patient_profile", oph_id=patient.oph_id)


# API: FHIR Patient Bundle Ingestion (POST)

@csrf_exempt
def api_fhir_ingest_patients(request):
    
    if request.method != "POST":
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload"}, status=400)

    if data.get("resourceType") != "Bundle":
        return JsonResponse({"error": "Payload must be a FHIR Bundle"}, status=400)

    entries = data.get("entry", [])
    created_patients = []
    errors = []

    for index, entry in enumerate(entries):
        resource = entry.get("resource", {})
        
        if resource.get("resourceType") != "Patient":
            continue

        try:
            name_node = resource.get("name", [{}])[0]
            last_name = name_node.get("family", "Unknown")
            first_name = " ".join(name_node.get("given", ["Unknown"]))

            identifiers = resource.get("identifier", [])
            national_id = identifiers[0].get("value", f"UNKNOWN-{random.randint(1000,9999)}") if identifiers else f"UNKNOWN-{random.randint(1000,9999)}"

            dob = resource.get("birthDate", "1900-01-01")
            
            fhir_gender = resource.get("gender", "Unknown").title()
            gender = "Male" if fhir_gender == "Male" else "Female"

            telecoms = resource.get("telecom", [{}])
            phone = telecoms[0].get("value", "0000000000") if telecoms else "0000000000"

            addresses = resource.get("address", [{}])
            address = addresses[0].get("text", "No address provided") if addresses else "No address provided"

            if not Patient.objects.filter(national_id=national_id).exists():
                patient = Patient.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    national_id=national_id,
                    date_of_birth=dob,
                    gender=gender,
                    phone_number=phone,
                    address=address
                )
                created_patients.append(patient.oph_id)
            else:
                errors.append(f"Entry {index}: Patient with National ID {national_id} already exists.")

        except Exception as e:
            errors.append(f"Entry {index}: Failed to parse - {str(e)}")

    return JsonResponse({
        "status": "success",
        "message": f"Successfully ingested {len(created_patients)} patients.",
        "created_oph_ids": created_patients,
        "errors": errors
    }, status=201)