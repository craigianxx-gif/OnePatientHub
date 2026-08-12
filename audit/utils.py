from .models import AuditLog


# ==========================================
# GET CLIENT IP ADDRESS
# ==========================================

def get_client_ip(request):

    x_forwarded_for = request.META.get(
        "HTTP_X_FORWARDED_FOR"
    )

    if x_forwarded_for:

        ip = x_forwarded_for.split(",")[0].strip()

    else:

        ip = request.META.get(

            "REMOTE_ADDR",

            None

        )

    return ip


# ==========================================
# CREATE AUDIT LOG
# ==========================================

def create_audit_log(

    request,

    action,

    module,

    description,

    object_id=None

):

    # Only create a log when a request exists

    if request is None:

        return None


    # Get authenticated user

    user = (

        request.user

        if request.user.is_authenticated

        else None

    )


    # Create audit log

    audit_log = AuditLog.objects.create(

        user=user,

        action=action,

        module=module,

        description=description,

        object_id=(

            str(object_id)

            if object_id is not None

            else None

        ),

        ip_address=get_client_ip(

            request

        )

    )


    return audit_log