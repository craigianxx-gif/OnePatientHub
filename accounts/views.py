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

            # ----------------------------------
            # AUDIT LOGIN
            # ----------------------------------

            create_audit_log(
                request=request,
                action="LOGIN",
                module="Authentication",
                description=(
                    f"User {user.username} "
                    "logged into OnePatient Hub."
                ),
                object_id=str(user.id)
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

    username = request.user.username

    user_id = request.user.id

    # ----------------------------------
    # AUDIT LOGOUT
    # ----------------------------------

    create_audit_log(
        request=request,
        action="LOGOUT",
        module="Authentication",
        description=(
            f"User {username} "
            "logged out of OnePatient Hub."
        ),
        object_id=str(user_id)
    )

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

    query = request.GET.get(
        "q",
        ""
    ).strip()

    module_filter = request.GET.get(
        "module",
        ""
    ).strip()

    logs = (
        AuditLog.objects
        .select_related("user")
        .all()
        .order_by("-timestamp")
    )

    # ----------------------------------
    # SEARCH FILTERING
    # ----------------------------------

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

        mapped_action = action_mapping.get(
            q_upper,
            q_upper
        )

        logs = logs.filter(
            Q(
                description__icontains=query
            )
            |
            Q(
                user__username__icontains=query
            )
            |
            Q(
                action__icontains=query
            )
            |
            Q(
                action__icontains=mapped_action
            )
            |
            Q(
                module__icontains=query
            )
            |
            Q(
                object_id__icontains=query
            )
        )

    # ----------------------------------
    # MODULE FILTER
    # ----------------------------------

    if module_filter:

        logs = logs.filter(
            module=module_filter
        )

    # ----------------------------------
    # MODULE LIST
    # ----------------------------------

    modules = (
        AuditLog.objects
        .order_by("module")
        .values_list(
            "module",
            flat=True
        )
        .distinct()
    )

    context = {

        "logs": logs,

        "query": request.GET.get(
            "q",
            ""
        ),

        "selected_module": (
            module_filter
        ),

        "modules": modules,

        "total_logs": logs.count(),

        "login_count": logs.filter(
            action="LOGIN"
        ).count(),

        "logout_count": logs.filter(
            action="LOGOUT"
        ).count(),

        "create_count": logs.filter(
            action="CREATE"
        ).count(),

        "update_count": logs.filter(
            action="UPDATE"
        ).count(),

        "delete_count": logs.filter(
            action="DELETE"
        ).count(),

        "export_count": logs.filter(
            action="EXPORT"
        ).count(),

        "other_count": logs.filter(
            action="OTHER"
        ).count(),
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
        AccountRequest.objects
        .all()
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

    # ======================================
    # ONLY ALLOW POST
    # ======================================

    if request.method != "POST":

        messages.error(
            request,
            "Invalid account approval request."
        )

        return redirect(
            "account_requests"
        )

    # ======================================
    # GET ACCOUNT REQUEST
    # ======================================

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
    # VALIDATE REQUIRED INFORMATION
    # ======================================

    if not account_request.email:

        messages.error(
            request,
            (
                "Account approval failed: "
                "applicant email is missing."
            )
        )

        return redirect(
            "account_requests"
        )

    if not account_request.staff_id:

        messages.error(
            request,
            (
                "Account approval failed: "
                "Staff ID is missing."
            )
        )

        return redirect(
            "account_requests"
        )

    if not account_request.full_name:

        messages.error(
            request,
            (
                "Account approval failed: "
                "applicant name is missing."
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
    # CHECK EXISTING USERNAME
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
    # CHECK EXISTING EMAIL
    # ======================================

    if User.objects.filter(
        email__iexact=account_request.email
    ).exists():

        messages.error(
            request,
            (
                "A user with this email "
                "address already exists."
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

        # ==================================
        # DATABASE TRANSACTION (USER CREATION)
        # ==================================

        with transaction.atomic():

            # ==============================
            # CREATE USER
            # ==============================

            user = User.objects.create_user(

                username=username,

                email=account_request.email,

                first_name=(
                    account_request
                    .full_name
                    .strip()
                    .split()[0]
                ),

                password=temporary_password

            )

            # ==============================
            # UPDATE OR CREATE USER PROFILE
            # ==============================

            UserProfile.objects.update_or_create(

                user=user,

                defaults={
                    "role": account_request.requested_role,
                    "country_code": "ZW",
                    "staff_id": account_request.staff_id,
                    "phone_number": account_request.phone_number,
                    "must_change_password": True
                }

            )

            # ==============================
            # MARK REQUEST AS APPROVED
            # ==============================

            account_request.status = (
                "approved"
            )

            account_request.save(
                update_fields=[
                    "status"
                ]
            )

            # ==============================
            # CREATE AUDIT LOG
            # ==============================

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

    except Exception as error:

        messages.error(

            request,

            (
                "Account approval failed during setup: "
                f"{error}"
            )

        )

        return redirect(
            "account_requests"
        )

    # ======================================
    # SEND CREDENTIALS EMAIL SEPARATELY
    # ======================================

    try:

        login_url = (
            request.build_absolute_uri("/")
        )

        email_html = render_to_string(

            "accounts/account_approved.html",

            {

                "account_request":
                    account_request,

                "user":
                    user,

                "temporary_password":
                    temporary_password,

                "login_url":
                    login_url,

            }

        )

        email_text = (

            f"Hello "
            f"{account_request.full_name},\n\n"

            "Your OnePatient Hub account "
            "has been approved.\n\n"

            "Username:\n"
            f"{username}\n\n"

            "Temporary Password:\n"
            f"{temporary_password}\n\n"

            "Login:\n"
            f"{login_url}\n\n"

            "For security reasons, you "
            "must change your temporary "
            "password after your first "
            "login.\n\n"

            "Regards,\n"
            "OnePatient Hub Administration"

        )

        email = EmailMultiAlternatives(

            subject=(
                "OnePatient Hub "
                "Account Approved"
            ),

            body=email_text,

            from_email=None,

            to=[
                account_request.email
            ]

        )

        email.attach_alternative(

            email_html,

            "text/html"

        )

        email.send(
            fail_silently=False
        )

    except Exception as email_error:

        messages.warning(

            request,

            (
                "Account approved successfully, "
                "but email dispatch failed: "
                f"{email_error}"
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

    # ======================================
    # ONLY ALLOW POST
    # ======================================

    if request.method != "POST":

        messages.error(
            request,
            "Invalid account denial request."
        )

        return redirect(
            "account_requests"
        )

    # ======================================
    # GET ACCOUNT REQUEST
    # ======================================

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

    account_request.save(
        update_fields=[
            "status"
        ]
    )

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

    # ======================================
    # SUCCESS MESSAGE
    # ======================================

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