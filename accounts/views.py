from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib.auth import (
    authenticate,
    login,
    logout
)

from django.contrib.auth.decorators import (
    login_required
)

from django.contrib.auth.models import User

from django.contrib import messages

from django.contrib.auth.hashers import (
    make_password
)

from django.db import transaction

from django.db.models import Q

from django.core.mail import (
    EmailMultiAlternatives
)

from django.template.loader import (
    render_to_string
)

import secrets

from .forms import AccountRequestForm

from .models import (
    AccountRequest,
    UserProfile
)

from audit.models import AuditLog

from audit.utils import (
    create_audit_log
)

from .decorators import (
    administrator_required
)

# ==========================================
# LOGIN
# ==========================================

def login_view(request):

    message = ""

    if request.method == "POST":

        username = request.POST.get(
            "username"
        )

        password = request.POST.get(
            "password"
        )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(
                request,
                user
            )
            return redirect(
                "dashboard"
            )
        else:
            message = (
                "Invalid username "
                "or password."
            )

    return render(
        request,
        "accounts/login.html",
        {
            "message": message
        }
    )

# ==========================================
# LOGOUT
# ==========================================

@login_required
def logout_view(request):

    logout(
        request
    )

    return redirect(
        "login"
    )

# ==========================================
# ACCOUNT REQUEST
# ==========================================

def request_account(request):

    if request.method == "POST":

        form = AccountRequestForm(
            request.POST
        )

        if form.is_valid():
            form.save()
            return redirect(
                "request_account_success"
            )

    else:
        form = AccountRequestForm()

    return render(
        request,
        "accounts/request_account.html",
        {
            "form": form
        }
    )

# ==========================================
# ACCOUNT REQUEST SUCCESS
# ==========================================

def request_account_success(request):

    return render(
        request,
        "accounts/request_success.html"
    )

# ==========================================
# AUDIT LOGS
# ADMINISTRATOR ONLY
# ==========================================

@login_required
@administrator_required
def audit_logs_view(request):

    query = request.GET.get("q", "").strip()
    module_filter = request.GET.get("module", "").strip()

    logs = (
        AuditLog.objects
        .select_related("user")
        .all()
        .order_by("-timestamp")
    )

    # Apply Search Filtering (Actions, Usernames, Descriptions, Modules, Object IDs)
    if query:
        q_upper = query.upper()
        action_mapping = {
            "ADD": "CREATE",
            "NEW": "CREATE",
            "EDIT": "UPDATE",
            "CHANGE": "UPDATE",
            "REMOVE": "DELETE",
            "DEL": "DELETE",
        }
        mapped_action = action_mapping.get(q_upper, q_upper)

        logs = logs.filter(
            Q(description__icontains=query) |
            Q(user__username__icontains=query) |
            Q(action__icontains=query) |
            Q(action__icontains=mapped_action) |
            Q(module__icontains=query) |
            Q(object_id__icontains=query)
        )

    # Apply Module Dropdown Filter
    if module_filter:
        logs = logs.filter(module=module_filter)

  # Get distinct modules for dropdown selection (clearing default ordering)
    modules = AuditLog.objects.order_by("module").values_list("module", flat=True).distinct()

    context = {
        "logs": logs,
        "query": request.GET.get("q", ""),
        "selected_module": module_filter,
        "modules": modules,
        "total_logs": logs.count(),
        "login_count": logs.filter(action="LOGIN").count(),
        "logout_count": logs.filter(action="LOGOUT").count(),
        "create_count": logs.filter(action="CREATE").count(),
        "update_count": logs.filter(action="UPDATE").count(),
        "delete_count": logs.filter(action="DELETE").count(),
        "export_count": logs.filter(action="EXPORT").count(),
        "other_count": logs.filter(action="OTHER").count(),
    }

    return render(
        request,
        "audit/audit_trail.html",
        context
    )

# ==========================================
# ACCOUNT REQUESTS
# ADMINISTRATOR ONLY
# ==========================================

@login_required
@administrator_required
def account_requests(request):

    requests = (
        AccountRequest.objects.all()
        .order_by(
            "-created_at"
        )
    )

    pending_count = (
        AccountRequest.objects.filter(
            status="pending"
        ).count()
    )

    approved_count = (
        AccountRequest.objects.filter(
            status="approved"
        ).count()
    )

    denied_count = (
        AccountRequest.objects.filter(
            status="denied"
        ).count()
    )

    return render(
        request,
        "accounts/account_requests.html",
        {
            "requests": requests,
            "pending_count": pending_count,
            "approved_count": approved_count,
            "denied_count": denied_count
        }
    )

# ==========================================
# APPROVE ACCOUNT REQUEST
# ADMINISTRATOR ONLY
# ==========================================

@login_required
@administrator_required
def approve_account_request(
    request,
    request_id
):

    account_request = get_object_or_404(
        AccountRequest,
        id=request_id
    )

    # ======================================
    # PREVENT DUPLICATE PROCESSING
    # ======================================

    if account_request.status != "pending":
        messages.warning(
            request,
            (
                "This account request "
                "has already been processed."
            )
        )
        return redirect(
            "account_requests"
        )

    # ======================================
    # CREATE USERNAME
    # ======================================

    username = (
        account_request.staff_id
        .strip()
        .lower()
    )

    # ======================================
    # CHECK EXISTING USER
    # ======================================

    if User.objects.filter(
        username=username
    ).exists():
        messages.error(
            request,
            (
                "A user with this Staff ID "
                "already exists."
            )
        )
        return redirect(
            "account_requests"
        )

    # ======================================
    # GENERATE TEMPORARY PASSWORD
    # ======================================

    temporary_password = (
        secrets.token_urlsafe(
            12
        )
    )

    try:
        with transaction.atomic():
            # ==================================
            # CREATE USER
            # ==================================
            user = User.objects.create_user(
                username=username,
                email=account_request.email,
                first_name=(
                    account_request.full_name
                    .split()[0]
                ),
                password=temporary_password
            )

            # ==================================
            # CREATE OR UPDATE USER PROFILE
            # ==================================
            UserProfile.objects.update_or_create(
                user=user,
                defaults={
                    "role": (
                        account_request
                        .requested_role
                    ),
                    "country_code": "ZW",
                    "staff_id": (
                        account_request
                        .staff_id
                    ),
                    "phone_number": (
                        account_request
                        .phone_number
                    )
                }
            )

            # ==================================
            # MARK REQUEST AS APPROVED
            # ==================================
            account_request.status = (
                "approved"
            )
            account_request.save()

            # ==================================
            # CREATE AUDIT LOG
            # ==================================
            create_audit_log(
                request=request,
                action="CREATE",
                module="Account Management",
                description=(
                    "Approved account request "
                    f"for "
                    f"{account_request.full_name}"
                ),
                object_id=str(
                    account_request.id
                )
            )

            # ==================================
            # PREPARE EMAIL
            # ==================================
            email_body = render_to_string(
                "emails/account_approved.txt",
                {
                    "full_name": (
                        account_request.full_name
                    ),
                    "username": username,
                    "temporary_password": (
                        temporary_password
                    )
                }
            )

            # ==================================
            # SEND EMAIL
            # ==================================
            email = EmailMultiAlternatives(
                subject=(
                    "OnePatient Hub Account Approved"
                ),
                body=email_body,
                from_email=None,
                to=[
                    account_request.email
                ]
            )

            email.send(
                fail_silently=False
            )

    except Exception as error:
        messages.error(
            request,
            (
                "Account approval failed: "
                f"{error}"
            )
        )
        return redirect(
            "account_requests"
        )

    # ======================================
    # SUCCESS MESSAGE
    # ======================================
    messages.success(
        request,
        (
            "Account approved successfully. "
            "Login credentials were sent to "
            f"{account_request.email}."
        )
    )

    return redirect(
        "account_requests"
    )

# ==========================================
# DENY ACCOUNT REQUEST
# ADMINISTRATOR ONLY
# ==========================================

@login_required
@administrator_required
def deny_account_request(
    request,
    request_id
):

    account_request = get_object_or_404(
        AccountRequest,
        id=request_id
    )

    # ======================================
    # PREVENT DUPLICATE PROCESSING
    # ======================================

    if account_request.status != "pending":
        messages.warning(
            request,
            (
                "This account request "
                "has already been processed."
            )
        )
        return redirect(
            "account_requests"
        )

    # ======================================
    # MARK AS DENIED
    # ======================================
    account_request.status = (
        "denied"
    )
    account_request.save()

    # ======================================
    # CREATE AUDIT LOG
    # ======================================
    create_audit_log(
        request=request,
        action="UPDATE",
        module="Account Management",
        description=(
            "Denied account request "
            f"for "
            f"{account_request.full_name}"
        ),
        object_id=str(
            account_request.id
        )
    )

    messages.success(
        request,
        (
            "Account request denied "
            "successfully."
        )
    )

    return redirect(
        "account_requests"
    )