
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ReferralForm
from .models import Referral
from patients.models import Patient
from audit.utils import create_audit_log
from notifications.models import ReferralNotification


def get_active_facility_id(request):
    return request.session.get("active_facility_id")


@login_required
def create_referral(request, oph_id):
    active_facility_id = get_active_facility_id(request)

    if not active_facility_id:
        messages.error(
            request,
            "Session expired or facility not selected. Please log in again.",
        )
        return redirect("login")

    patient = get_object_or_404(Patient, oph_id=oph_id)

    if request.method == "POST":
        form = ReferralForm(
            request.POST,
            active_facility_id=active_facility_id,
        )

        if form.is_valid():
            with transaction.atomic():
                referral = form.save(commit=False)
                referral.patient = patient
                referral.referring_facility_id = active_facility_id
                referral.created_by = request.user
                referral.save()

                if referral.receiving_facility_id:
                    ReferralNotification.objects.create(
                        referral=referral,
                        facility_id=referral.receiving_facility_id,
                        message=(
                            "A new referral is awaiting review from "
                            f"{referral.referring_facility.facility_name}."
                        ),
                    )

                create_audit_log(
                    request=request,
                    action="CREATE",
                    module="Referrals",
                    description=(
                        "Created referral to "
                        f"{referral.receiving_facility.facility_name} "
                        f"for patient {referral.patient.oph_id}"
                    ),
                    object_id=str(referral.id),
                )

            messages.success(
                request,
                "Referral sent successfully.",
            )
            return redirect("referral_list")

    else:
        form = ReferralForm(
            active_facility_id=active_facility_id,
        )

    return render(
        request,
        "referrals/create_referral.html",
        {
            "form": form,
            "patient": patient,
        },
    )


@login_required
def referral_success(request):
    return render(
        request,
        "referrals/referral_success.html",
    )


@login_required
def referral_list(request):
    active_facility_id = get_active_facility_id(request)

    if not active_facility_id:
        messages.error(request, "Please select a facility first.")
        return redirect("login")

    query = request.GET.get("q", "").strip()

    referrals = Referral.objects.filter(
        Q(referring_facility_id=active_facility_id)
        | Q(receiving_facility_id=active_facility_id)
    ).select_related(
        "patient",
        "referring_facility",
        "receiving_facility",
    ).order_by("-created_at")

    if query:
        referrals = referrals.filter(
            Q(patient__oph_id__icontains=query)
            | Q(patient__first_name__icontains=query)
            | Q(patient__last_name__icontains=query)
            | Q(
                referring_facility__facility_name__icontains=query
            )
            | Q(
                receiving_facility__facility_name__icontains=query
            )
        )

    pending_incoming = referrals.filter(
        receiving_facility_id=active_facility_id,
        status="Pending",
    ).count()

    return render(
        request,
        "referrals/referral_list.html",
        {
            "referrals": referrals,
            "query": query,
            "active_facility_id": int(active_facility_id),
            "pending_incoming": pending_incoming,
        },
    )


@login_required
def update_referral_status(request, referral_id):
    active_facility_id = get_active_facility_id(request)

    if not active_facility_id:
        messages.error(request, "Please select a facility first.")
        return redirect("login")

    if request.method != "POST":
        return redirect("referral_list")

    referral = get_object_or_404(
        Referral.objects.select_related(
            "patient",
            "referring_facility",
            "receiving_facility",
        ).filter(
            Q(receiving_facility_id=active_facility_id)
            | Q(referring_facility_id=active_facility_id)
        ),
        id=referral_id,
    )

    new_status = request.POST.get("status")
    valid_statuses = dict(Referral.STATUS_CHOICES)

    if new_status not in valid_statuses:
        messages.error(request, "Invalid status update requested.")
        return redirect("referral_list")

    is_receiver = (
        str(referral.receiving_facility_id)
        == str(active_facility_id)
    )
    is_sender = (
        str(referral.referring_facility_id)
        == str(active_facility_id)
    )

    old_status = referral.status
    status_updated = False

    # Receiving facility accepts a pending referral.
    if is_receiver and old_status == "Pending" and new_status == "Accepted":
        referral.status = new_status
        status_updated = True

    # Receiving facility completes an accepted referral.
    elif (
        is_receiver
        and old_status == "Accepted"
        and new_status == "Completed"
    ):
        referral.status = new_status
        status_updated = True

    # Referring facility may cancel a referral while pending.
    elif (
        is_sender
        and old_status == "Pending"
        and new_status == "Cancelled"
    ):
        referral.status = new_status
        status_updated = True

    if not status_updated:
        messages.error(
            request,
            "You are not permitted to make that status change, "
            "or the referral is not in the required status.",
        )
        return redirect("referral_list")

    referral.save(update_fields=["status"])

    create_audit_log(
        request=request,
        action="UPDATE",
        module="Referrals",
        description=(
            f"Referral {referral.id} status changed "
            f"from {old_status} to {new_status}"
        ),
        object_id=str(referral.id),
    )

    messages.success(
        request,
        f"Referral status updated to {new_status}.",
    )

    return redirect("referral_list")


@login_required
def referral_detail(request, referral_id):
    active_facility_id = get_active_facility_id(request)

    if not active_facility_id:
        messages.error(request, "Please select a facility first.")
        return redirect("login")

    referral = get_object_or_404(
        Referral.objects.select_related(
            "patient",
            "referring_facility",
            "receiving_facility",
            "created_by",
        ).filter(
            Q(referring_facility_id=active_facility_id)
            | Q(receiving_facility_id=active_facility_id)
        ),
        id=referral_id,
    )

    is_sender = (
        str(referral.referring_facility_id)
        == str(active_facility_id)
    )
    is_receiver = (
        str(referral.receiving_facility_id)
        == str(active_facility_id)
    )

    create_audit_log(
        request=request,
        action="VIEW",
        module="Referrals",
        description=(
            f"Viewed referral {referral.id} "
            f"(Patient: {referral.patient.oph_id})"
        ),
        object_id=str(referral.id),
    )

    return render(
        request,
        "referrals/referral_detail.html",
        {
            "referral": referral,
            "active_facility_id": int(active_facility_id),
            "is_receiver": is_receiver,
            "is_sender": is_sender,
        },
    )
