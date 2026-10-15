
from .models import ReferralNotification, NotificationRead


def referral_notification_count(request):
    if not request.user.is_authenticated:
        return {"unread_referral_count": 0}

    facility_id = request.session.get("active_facility_id")

    if not facility_id:
        return {"unread_referral_count": 0}

    notifications = ReferralNotification.objects.filter(
        facility_id=facility_id
    )

    read_notifications = NotificationRead.objects.filter(
        user=request.user,
        notification__facility_id=facility_id,
    ).values("notification_id")

    unread_count = notifications.exclude(
        id__in=read_notifications
    ).count()

    return {"unread_referral_count": unread_count}
