
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import ReferralNotification, NotificationRead


@login_required
def notification_list(request):
    active_facility_id = request.session.get("active_facility_id")

    if not active_facility_id:
        messages.error(request, "Please select a facility first.")
        return redirect("login")

    notifications = ReferralNotification.objects.filter(
        facility_id=active_facility_id
    ).select_related(
        "referral",
        "referral__patient",
        "referral__referring_facility",
    )

    read_ids = NotificationRead.objects.filter(
        user=request.user,
        notification__facility_id=active_facility_id
    ).values_list("notification_id", flat=True)

    unread_count = notifications.exclude(id__in=read_ids).count()

    return render(
        request,
        "notifications/notification_list.html",
        {
            "notifications": notifications,
            "read_ids": list(read_ids),
            "unread_count": unread_count,
        }
    )


@login_required
def open_notification(request, notification_id):
    active_facility_id = request.session.get("active_facility_id")

    if not active_facility_id:
        return redirect("login")

    notification = get_object_or_404(
        ReferralNotification.objects.select_related("referral"),
        id=notification_id,
        facility_id=active_facility_id,
    )

    NotificationRead.objects.get_or_create(
        notification=notification,
        user=request.user,
    )

    return redirect(
        "referral_detail",
        referral_id=notification.referral_id
    )
