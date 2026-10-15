from .models import AuditLog

def get_client_ip(request):
    """
    Utility function to extract the client's IP address from the request.
    Handles environments behind proxies or load balancers.
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR")

    return ip

def create_audit_log(request, action, module, description, object_id=None):
    """
    Creates an immutable audit log entry for system actions.
    Ensures the user is authenticated before logging to prevent anonymous errors.
    """
    if request and hasattr(request, 'user') and request.user.is_authenticated:
        AuditLog.objects.create(
            user=request.user,
            action=action,
            module=module,
            description=description,
            object_id=object_id,
            ip_address=get_client_ip(request)
        )