from django.shortcuts import (
    render,
    get_object_or_404,
    redirect
)
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone  # NEW: Required for date checking

from patients.models import Patient
from audit.utils import create_audit_log

from .models import PatientConsent
from .forms import PatientConsentForm


# ==========================================
# CONSENT LIST
# ==========================================

@login_required
def consent_list(request):

    consents = PatientConsent.objects.select_related(
        "patient"
    ).order_by(
        "-created_at"
    )

    return render(
        request,
        "consent/consent_list.html",
        {
            "consents": consents
        }
    )


# ==========================================
# MANAGE PATIENT CONSENT
# ==========================================

@login_required
def manage_consent(request, oph_id):

    patient = get_object_or_404(
        Patient,
        oph_id=oph_id
    )

    consent = PatientConsent.objects.filter(
        patient=patient
    ).first()

    # ==========================================
    # NEW: AUTO-EXPIRE STALE CONSENT ON LOAD
    # ==========================================
    if consent and consent.expiry_date and consent.status in ["Granted", "Active", "Yes"]:
        if consent.expiry_date < timezone.now().date():
            consent.status = "Expired"  # Force status to expired
            consent.save()
            messages.warning(
                request, 
                f"⚠️ Consent for {patient.first_name} expired on {consent.expiry_date.strftime('%d %b %Y')}. Status has been automatically updated."
            )

    if request.method == "POST":

        form = PatientConsentForm(
            request.POST,
            request.FILES,
            instance=consent
        )

        if form.is_valid():

            new_consent = form.save(
                commit=False
            )

            new_consent.patient = patient
            new_consent.created_by = request.user

            # ==========================================
            # NEW: PREVENT SAVING 'GRANTED' IF DATE IS PAST
            # ==========================================
            if new_consent.expiry_date and new_consent.expiry_date < timezone.now().date():
                new_consent.status = "Expired"
                messages.warning(
                    request, 
                    "The expiry date provided is in the past. Consent automatically set to Expired."
                )
            else:
                messages.success(request, "Patient consent preferences successfully updated.")

            new_consent.save()

            create_audit_log(
                request=request,
                action="UPDATE",
                module="Consent Management",
                description=(
                    f"Updated consent for {patient.oph_id}. "
                    f"Status: {new_consent.status}"
                ),
                object_id=patient.oph_id
            )

            return redirect(
                "patient_profile",
                oph_id=patient.oph_id
            )
            
        else:
            print("\n====================================")
            print("❌ CONSENT FORM VALIDATION FAILED ❌")
            print(form.errors)
            print("====================================\n")
            messages.error(request, "Failed to save consent. Please check the form inputs.")

    else:

        form = PatientConsentForm(
            instance=consent
        )

    return render(
        request,
        "consent/manage_consent.html",
        {
            "patient": patient,
            "form": form,
            "consent": consent
        }
    )