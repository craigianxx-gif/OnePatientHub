import random

from django.shortcuts import (
    render,
    get_object_or_404,
    redirect
)

from django.contrib.auth.decorators import login_required

from django.db.models import Q

from django.contrib import messages

from audit.utils import create_audit_log

from consent.models import PatientConsent

from .forms import (
    PatientForm,
    ExternalPatientIdentifierForm
)

from .models import Patient


# ==========================================
# OPH-ID GENERATION
# ==========================================

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
    Generates an OPH-ID in the format:

    ZW-4512-0876-3
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


# ==========================================
# REGISTER PATIENT
# ==========================================

@login_required
def register_patient(request):

    if request.method == "POST":

        form = PatientForm(
            request.POST
        )

        if form.is_valid():

            patient = form.save(
                commit=False
            )

            # Get country code from user profile
            try:

                country_code = (

                    request.user.profile.country_code

                    or "ZW"

                )

            except AttributeError:

                country_code = "ZW"

            # Generate OPH-ID
            patient.oph_id = generate_oph_id(

                country_code

            )

            # Save patient
            patient.save()

            # Audit patient registration
            create_audit_log(

                request=request,

                action="CREATE",

                module="Patients",

                description=(

                    f"Registered patient "

                    f"{patient.oph_id}"

                ),

                object_id=patient.oph_id

            )

            # Redirect to patient profile
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


# ==========================================
# PATIENT DIRECTORY
# ==========================================

@login_required
def patient_records(request):

    query = request.GET.get(

        "q",

        ""

    )

    patients = (

        Patient.objects.all()

        .order_by(

            "-created_at"

        )

    )

    if query:

        patients = patients.filter(

            Q(

                oph_id__icontains=query

            )

            |

            Q(

                national_id__icontains=query

            )

            |

            Q(

                first_name__icontains=query

            )

            |

            Q(

                last_name__icontains=query

            )

        )

    return render(

        request,

        "patients/patient_records.html",

        {

            "patients": patients,

            "query": query

        }

    )


# ==========================================
# PATIENT PROFILE
# ==========================================

@login_required
def patient_profile(

    request,

    oph_id

):

    patient = get_object_or_404(

        Patient,

        oph_id=oph_id

    )

    # ======================================
    # EXISTING PATIENT RECORDS
    # ======================================

    visits = (

        patient.visits.all()

        .order_by(

            "-visit_date"

        )

    )

    referrals = (

        patient.referrals.all()

        .order_by(

            "-created_at"

        )

    )

    external_identifiers = (

        patient.external_identifiers.all()

        .order_by(

            "-created_at"

        )

    )

    # ======================================
    # PATIENT JOURNEY TIMELINE
    # ======================================

    timeline_events = []

    # --------------------------------------
    # 1. PATIENT REGISTRATION
    # --------------------------------------

    timeline_events.append({

        "event_type": "Patient Registered",

        "event_category": "registration",

        "date": patient.created_at,

        "facility": "OnePatient Hub",

        "description": (

            "Patient identity created in "

            "the OnePatient Hub identity registry."

        ),

        "status": "Completed",

        "icon": "user"

    })

    # --------------------------------------
    # 2. HEALTHCARE VISITS
    # --------------------------------------

    for visit in visits:

        timeline_events.append({

            "event_type": "Healthcare Visit",

            "event_category": "visit",

            "date": visit.visit_date,

            "facility": visit.facility_name,

            "description": (

                f"{visit.visit_type}: "

                f"{visit.reason}"

            ),

            "status": "Completed",

            "icon": "calendar"

        })

    # --------------------------------------
    # 3. REFERRALS
    # --------------------------------------

    for referral in referrals:

        timeline_events.append({

            "event_type": "Patient Referral",

            "event_category": "referral",

            "date": referral.referral_date,

            "facility": (

                f"{referral.referring_facility} "

                f"→ "

                f"{referral.receiving_facility}"

            ),

            "description": referral.reason,

            "status": referral.status,

            "icon": "arrow"

        })

    # --------------------------------------
    # 4. EXTERNAL IDENTIFIERS
    # --------------------------------------

    for identifier in external_identifiers:

        timeline_events.append({

            "event_type": (

                "External Identifier Linked"

            ),

            "event_category": "identity",

            "date": identifier.created_at,

            "facility": identifier.facility_name,

            "description": (

                f"System: "

                f"{identifier.system_name} "

                f"| Identifier: "

                f"{identifier.identifier}"

            ),

            "status": "Linked",

            "icon": "link"

        })

    # ======================================
    # SORT TIMELINE
    # ======================================

    timeline_events.sort(

        key=lambda event: event["date"],

        reverse=True

    )

    # ======================================
    # AUDIT PATIENT PROFILE ACCESS
    # ======================================

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

    # ======================================
    # RENDER PATIENT PROFILE
    # ======================================

    return render(

        request,

        "patients/patient_profile.html",

        {

            "patient": patient,

            "visits": visits,

            "referrals": referrals,

            "external_identifiers":

                external_identifiers,

            "timeline_events":

                timeline_events

        }

    )


# ==========================================
# ADD EXTERNAL IDENTIFIER
# ==========================================

@login_required
def add_external_identifier(

    request,

    oph_id

):

    patient = get_object_or_404(

        Patient,

        oph_id=oph_id

    )

    if request.method == "POST":

        form = (

            ExternalPatientIdentifierForm(

                request.POST

            )

        )

        if form.is_valid():

            external_identifier = form.save(

                commit=False

            )

            external_identifier.patient = (

                patient

            )

            external_identifier.save()

            # Audit external identifier creation
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

        form = (

            ExternalPatientIdentifierForm()

        )

    return render(

        request,

        "patients/add_external_identifier.html",

        {

            "patient": patient,

            "form": form

        }

    )


# ==========================================
# EDIT PATIENT
# ==========================================

@login_required
def edit_patient(

    request,

    oph_id

):

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

            # Audit patient update
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

        form = PatientForm(

            instance=patient

        )

    return render(

        request,

        "patients/edit_patient.html",

        {

            "form": form,

            "patient": patient

        }

    )


# ==========================================
# DELETE PATIENT
# ==========================================

@login_required
def delete_patient(

    request,

    oph_id

):

    patient = get_object_or_404(

        Patient,

        oph_id=oph_id

    )

    if request.method == "POST":

        patient_oph_id = patient.oph_id

        # Audit deletion BEFORE deleting patient
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

        return redirect(

            "patient_directory"

        )

    return render(

        request,

        "patients/delete_patient.html",

        {

            "patient": patient

        }

    )


# ==========================================
# PATIENT JOURNEY / HORIZONTAL TRACKING
# ==========================================

@login_required
def patient_journey(

    request,

    oph_id

):

    patient = get_object_or_404(

        Patient,

        oph_id=oph_id

    )

    consent = PatientConsent.objects.filter(
        patient=patient
    ).first()

    is_emergency_override = request.session.get(
        f'emergency_override_{oph_id}',
        False
    )

    if (not consent or not consent.is_granted) and not is_emergency_override:
        messages.warning(
            request,
            "Access restricted: Patient has not granted data sharing consent."
        )
        return redirect(
            'patient_profile',
            oph_id=patient.oph_id
        )

    visits = (

        patient.visits.all()

        .order_by(

            "-visit_date"

        )

    )

    referrals = (

        patient.referrals.all()

        .order_by(

            "-referral_date"

        )

    )

    external_identifiers = (

        patient.external_identifiers.all()

        .order_by(

            "-created_at"

        )

    )

    timeline_events = []

    # --------------------------------------
    # PATIENT REGISTRATION
    # --------------------------------------

    timeline_events.append({

        "event_type": "Patient Registered",

        "event_category": "registration",

        "date": patient.created_at,

        "facility": "OnePatient Hub",

        "description": (

            "Patient identity created in "

            "the OnePatient Hub identity registry."

        ),

        "status": "Completed",

        "icon": "user"

    })

    # --------------------------------------
    # HEALTHCARE VISITS
    # --------------------------------------

    for visit in visits:

        timeline_events.append({

            "event_type": "Healthcare Visit",

            "event_category": "visit",

            "date": visit.visit_date,

            "facility": visit.facility_name,

            "description": (

                f"{visit.visit_type}: "

                f"{visit.reason}"

            ),

            "status": "Completed",

            "icon": "calendar"

        })

    # --------------------------------------
    # REFERRALS
    # --------------------------------------

    for referral in referrals:

        timeline_events.append({

            "event_type": "Patient Referral",

            "event_category": "referral",

            "date": referral.referral_date,

            "facility": (

                f"{referral.referring_facility} "

                f"→ "

                f"{referral.receiving_facility}"

            ),

            "description": referral.reason,

            "status": referral.status,

            "icon": "arrow"

        })

    # --------------------------------------
    # EXTERNAL IDENTIFIERS
    # --------------------------------------

    for identifier in external_identifiers:

        timeline_events.append({

            "event_type": (

                "External Identifier Linked"

            ),

            "event_category": "identity",

            "date": identifier.created_at,

            "facility": identifier.facility_name,

            "description": (

                f"System: "

                f"{identifier.system_name} "

                f"| Identifier: "

                f"{identifier.identifier}"

            ),

            "status": "Linked",

            "icon": "link"

        })

    # --------------------------------------
    # SORT TIMELINE
    # --------------------------------------

    timeline_events.sort(

        key=lambda event: event["date"],

        reverse=True

    )

    # --------------------------------------
    # AUDIT LOG
    # --------------------------------------

    create_audit_log(

        request=request,

        action="VIEW",

        module="Patient Journey",

        description=(

            f"Viewed patient journey "

            f"{patient.oph_id}"

        ),

        object_id=patient.oph_id

    )

    return render(

        request,

        "patients/patient_journey.html",

        {

            "patient": patient,

            "timeline_events":

                timeline_events

        }

    )


# ==========================================
# EMERGENCY OVERRIDE
# ==========================================

@login_required
def trigger_emergency_override(request, oph_id):
    patient = get_object_or_404(Patient, oph_id=oph_id)
    
    if request.method == "POST":
        reason = request.POST.get("override_reason", "No reason provided")
        
        # Enable override in session for this specific patient
        request.session[f'emergency_override_{oph_id}'] = True
        
        # Log the critical override event
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
        
        messages.error(
            request,
            "⚠️ Emergency override active. Access granted for clinical emergency."
        )
        
        return redirect("patient_journey", oph_id=patient.oph_id)
        
    return render(
        request,
        "patients/emergency_override.html",
        {"patient": patient}
    )