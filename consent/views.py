from django.shortcuts import (
    render,
    get_object_or_404,
    redirect
)

from django.contrib.auth.decorators import login_required

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
def manage_consent(

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

    if request.method == "POST":

        form = PatientConsentForm(

            request.POST,

            instance=consent

        )

        if form.is_valid():

            consent = form.save(

                commit=False

            )

            consent.patient = patient

            consent.created_by = request.user

            consent.save()

            create_audit_log(

                request=request,

                action="UPDATE",

                module="Consent Management",

                description=(

                    f"Updated consent for "

                    f"{patient.oph_id}"

                ),

                object_id=patient.oph_id

            )

            return redirect(

                "patient_profile",

                oph_id=patient.oph_id

            )

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