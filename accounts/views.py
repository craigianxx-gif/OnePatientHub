from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib.auth import (
    authenticate,
    login,
    logout,
    update_session_auth_hash
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

from django.contrib.auth.forms import PasswordChangeForm

from facilities.models import Facility


# ==========================================
# LOGIN
# ==========================================

def login_view(request):

    message = ""
    facilities = Facility.objects.filter(is_active=True).order_by("facility_name")

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")
        facility_id = request.POST.get("facility_id")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            profile = getattr(user, 'profile', None)
            
            # --- SECURITY GATE: Verify facility authorization (Bypassed for master user craigianxx) ---
            if user.username != "craigianxx":
                if not profile or not profile.facility or str(profile.facility.id) != str(facility_id):
                    message = "Access Denied: You are not authorized to log into the selected facility."
                    return render(
                        request, 
                        "accounts/login.html", 
                        {
                            "message": message, 
                            "facilities": facilities
                        }
                    )

            # --- SECURITY GATE: Verify user is active ---
            if not user.is_active:
                message = "Access Denied: Your account has been deactivated."
                return render(
                    request, 
                    "accounts/login.html", 
                    {
                        "message": message, 
                        "facilities": facilities
                    }
                )

            login(request, user)
            
            # --- SET SESSION CONTEXT ---
            request.session['active_facility_id'] = facility_id
            
            # Handle facility name safely if profile.facility is None for master user
            facility_name = "Global / Master Session"
            if profile and profile.facility and str(profile.facility.id) == str(facility_id):
                facility_name = profile.facility.facility_name
            else:
                selected_facility = Facility.objects.filter(id=facility_id).first()
                if selected_facility:
                    facility_name = selected_facility.facility_name

            request.session['active_facility_name'] = facility_name

            create_audit_log(
                request=request,
                action="LOGIN",
                module="Authentication",
                description=(
                    f"User {user.username} "
                    f"logged in under {facility_name}."
                ),
                object_id=str(user.id)
            )

            return redirect("dashboard")

        else:
            message = "Invalid username or password."

    return render(
        request,
        "accounts/login.html",
        {
            "message": message,
            "facilities": facilities
        }
    )


# ==========================================
# LOGOUT
# ==========================================

@login_required
def logout_view(request):

    username = request.user.username
    user_id = request.user.id

    create_audit_log(
        request=request,
        action="LOGOUT",
        module="Authentication",
        description=f"User {username} logged out of OnePatient Hub.",
        object_id=str(user_id)
    )
    
    if 'active_facility_id' in request.session:
        del request.session['active_facility_id']
    if 'active_facility_name' in request.session:
        del request.session['active_facility_name']

    logout(request)
    return redirect("login")


# ==========================================
# ACCOUNT REQUEST
# ==========================================

def request_account(request):
    facilities = Facility.objects.filter(is_active=True).order_by("facility_name")

    if request.method == "POST":
        form = AccountRequestForm(request.POST)
        facility_id = request.POST.get("facility_id")

        if form.is_valid() and facility_id:
            account_request = form.save(commit=False)
            facility = get_object_or_404(Facility, id=facility_id)
            account_request.facility = facility
            account_request.save()
            return redirect("request_account_success")
        else:
            # Catch and display exact form validation errors
            if not facility_id:
                messages.error(request, "Please select a Healthcare Facility.")
                
            for field, errors in form.errors.items():
                for error in errors:
                    # Formats field names cleanly (e.g., 'staff_id' -> 'Staff Id')
                    clean_field = field.replace('_', ' ').title() 
                    messages.error(request, f"{clean_field}: {error}")
    else:
        form = AccountRequestForm()

    return render(
        request,
        "accounts/request_account.html",
        {
            "form": form,
            "facilities": facilities
        }
    )


# ==========================================
# ACCOUNT REQUEST SUCCESS
# ==========================================

def request_account_success(request):
    return render(request, "accounts/request_success.html")


# ==========================================
# AUDIT LOGS
# ==========================================

@login_required
@administrator_required
def audit_logs_view(request):
    query = request.GET.get("q", "").strip()
    module_filter = request.GET.get("module", "").strip()

    logs = AuditLog.objects.select_related("user").all().order_by("-timestamp")

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

    if module_filter:
        logs = logs.filter(module=module_filter)

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
    return render(request, "audit/audit_trail.html", context)


# ==========================================
# ACCOUNT REQUESTS
# ==========================================

@login_required
@administrator_required
def account_requests(request):
    # MASTER USER OVERRIDE: craigianxx sees all facility requests globally
    if request.user.username == "craigianxx":
        requests_qs = AccountRequest.objects.all().order_by("-created_at")
    else:
        active_facility_id = request.session.get('active_facility_id')
        
        if not active_facility_id:
            messages.error(request, "Session expired. Please log in again.")
            return redirect("login")

        requests_qs = AccountRequest.objects.filter(facility_id=active_facility_id).order_by("-created_at")

    pending_count = requests_qs.filter(status="pending").count()
    approved_count = requests_qs.filter(status="approved").count()
    denied_count = requests_qs.filter(status="denied").count()

    return render(
        request,
        "accounts/account_requests.html",
        {
            "requests": requests_qs,
            "pending_count": pending_count,
            "approved_count": approved_count,
            "denied_count": denied_count
        }
    )


# ==========================================
# FACILITY USERS (ACTIVE STAFF)
# ==========================================

@login_required
@administrator_required
def facility_users(request):
    active_facility_id = request.session.get('active_facility_id')
    
    if not active_facility_id:
        messages.error(request, "Session expired. Please log in again.")
        return redirect("login")

    staff_members = UserProfile.objects.filter(
        facility_id=active_facility_id
    ).select_related('user').order_by("-created_at")

    return render(
        request,
        "accounts/facility_users.html",
        {
            "staff_members": staff_members,
        }
    )


# ==========================================
# APPROVE ACCOUNT REQUEST
# ==========================================

@login_required
@administrator_required
def approve_account_request(request, request_id):
    if request.method != "POST":
        messages.error(request, "Invalid account approval request.")
        return redirect("account_requests")

    account_request = get_object_or_404(AccountRequest, id=request_id)
    active_facility_id = request.session.get('active_facility_id')

    if request.user.username != "craigianxx":
        if str(account_request.facility_id) != str(active_facility_id):
            messages.error(request, "Security Exception: You cannot approve staff for a different facility.")
            return redirect("account_requests")

    if account_request.status != "pending":
        messages.warning(request, "This account request has already been processed.")
        return redirect("account_requests")

    if not account_request.email or not account_request.staff_id or not account_request.full_name:
        messages.error(request, "Account approval failed: Missing applicant information.")
        return redirect("account_requests")

    username = account_request.staff_id.strip().lower()

    if User.objects.filter(username=username).exists():
        messages.error(request, "A user with this Staff ID already exists.")
        return redirect("account_requests")

    if User.objects.filter(email__iexact=account_request.email).exists():
        messages.error(request, "A user with this email address already exists.")
        return redirect("account_requests")

    temporary_password = "ChangeMe123!"

    try:
        with transaction.atomic():
            user = User.objects.create_user(
                username=username,
                email=account_request.email,
                first_name=account_request.full_name.strip().split()[0],
                password=temporary_password
            )

            UserProfile.objects.update_or_create(
                user=user,
                defaults={
                    "role": account_request.requested_role,
                    "country_code": "ZW",
                    "staff_id": account_request.staff_id,
                    "phone_number": account_request.phone_number,
                    "must_change_password": True,
                    "facility": account_request.facility
                }
            )

            account_request.status = "approved"
            account_request.save(update_fields=["status"])

            create_audit_log(
                request=request,
                action="CREATE",
                module="Account Management",
                description=f"Approved account request for {account_request.full_name}",
                object_id=str(account_request.id)
            )

    except Exception as error:
        messages.error(request, f"Account approval failed during setup: {error}")
        return redirect("account_requests")

    messages.success(request, f"Account for {account_request.full_name} approved successfully. They can log in using their Staff ID and the default password.")
    return redirect("account_requests")


# ==========================================
# DENY ACCOUNT REQUEST
# ==========================================

@login_required
@administrator_required
def deny_account_request(request, request_id):
    if request.method != "POST":
        messages.error(request, "Invalid account denial request.")
        return redirect("account_requests")

    account_request = get_object_or_404(AccountRequest, id=request_id)
    active_facility_id = request.session.get('active_facility_id')

    if request.user.username != "craigianxx":
        if str(account_request.facility_id) != str(active_facility_id):
            messages.error(request, "Security Exception: You cannot deny staff for a different facility.")
            return redirect("account_requests")

    if account_request.status != "pending":
        messages.warning(request, "This account request has already been processed.")
        return redirect("account_requests")

    account_request.status = "denied"
    account_request.save(update_fields=["status"])

    create_audit_log(
        request=request,
        action="UPDATE",
        module="Account Management",
        description=f"Denied account request for {account_request.full_name}",
        object_id=str(account_request.id)
    )

    messages.success(request, "Account request denied successfully.")
    return redirect("account_requests")


# ==========================================
# SETTINGS
# ==========================================

@login_required
def settings_view(request):
    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={"role": "nurse", "country_code": "ZW"}
    )
    return render(request, "accounts/settings.html", {"profile": profile})


# ==========================================
# PROFILE SETTINGS
# ==========================================

@login_required
def profile_settings(request):
    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={"role": "nurse", "country_code": "ZW"}
    )

    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        phone_number = request.POST.get("phone_number", "").strip()

        if not first_name:
            messages.error(request, "First name is required.")
            return redirect("profile_settings")

        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.save(update_fields=["first_name", "last_name"])

        profile.phone_number = phone_number
        profile.save(update_fields=["phone_number"])

        create_audit_log(
            request=request,
            action="UPDATE",
            module="Account Settings",
            description=f"User {request.user.username} updated their profile.",
            object_id=str(request.user.id)
        )

        messages.success(request, "Profile updated successfully.")
        return redirect("profile_settings")

    return render(request, "accounts/profile_settings.html", {"profile": profile})


# ==========================================
# PASSWORD SETTINGS
# ==========================================

@login_required
def password_settings(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            profile, created = UserProfile.objects.get_or_create(
                user=user, defaults={"role": "nurse", "country_code": "ZW"}
            )
            profile.must_change_password = False
            profile.save(update_fields=["must_change_password"])

            create_audit_log(
                request=request,
                action="UPDATE",
                module="Account Settings",
                description=f"User {user.username} changed their password.",
                object_id=str(user.id)
            )

            messages.success(request, "Your password has been changed successfully.")
            return redirect("settings")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, "accounts/password_settings.html", {"form": form})


# ============================================================
# LEGAL
# ============================================================

def terms_of_use(request):
    return render(request, "accounts/terms_of_use.html")

def privacy_statement(request):
    return render(request, "accounts/privacy_statement.html")

def software_services_agreement(request):
    return render(request, "accounts/software_services_agreement.html")


# ============================================================
# SESSION LOADER
# ============================================================

@login_required
def session_loader(request):
    return render(request, "accounts/session_loader.html")


# ==========================================
# REMOVE FACILITY USER
# ==========================================

@login_required
@administrator_required
def remove_facility_user(request, user_id):
    if request.method != "POST":
        messages.error(request, "Invalid request.")
        return redirect("facility_users")

    active_facility_id = request.session.get('active_facility_id')
    target_profile = get_object_or_404(UserProfile, user_id=user_id)

    if request.user.id == target_profile.user.id:
        messages.error(request, "You cannot revoke your own access.")
        return redirect("facility_users")

    if request.user.username != "craigianxx":
        if str(target_profile.facility_id) != str(active_facility_id):
            messages.error(request, "Security Exception: You cannot remove staff from a different facility.")
            return redirect("facility_users")

    target_profile.facility = None
    target_profile.save(update_fields=["facility"])

    create_audit_log(
        request=request,
        action="UPDATE",
        module="Account Management",
        description=f"Removed facility access for user {target_profile.user.username}",
        object_id=str(target_profile.user.id)
    )

    messages.success(request, f"Access revoked. {target_profile.user.first_name} removed from facility.")
    return redirect("facility_users")


# ==========================================
# DEACTIVATE FACILITY USER
# ==========================================

@login_required
@administrator_required
def deactivate_facility_user(request, user_id):
    if request.method != "POST":
        messages.error(request, "Invalid request.")
        return redirect("facility_users")

    active_facility_id = request.session.get('active_facility_id')
    target_profile = get_object_or_404(UserProfile, user_id=user_id)

    if request.user.id == target_profile.user.id:
        messages.error(request, "You cannot deactivate your own account.")
        return redirect("facility_users")

    if request.user.username != "craigianxx":
        if str(target_profile.facility_id) != str(active_facility_id):
            messages.error(request, "Security Exception: You cannot modify staff from a different facility.")
            return redirect("facility_users")

    target_profile.user.is_active = False
    target_profile.user.save(update_fields=["is_active"])

    create_audit_log(
        request=request,
        action="UPDATE",
        module="Account Management",
        description=f"Deactivated user {target_profile.user.username}",
        object_id=str(target_profile.user.id)
    )

    messages.success(request, f"Account for {target_profile.user.first_name} deactivated successfully.")
    return redirect("facility_users")


# ==========================================
# ACTIVATE FACILITY USER
# ==========================================

@login_required
@administrator_required
def activate_facility_user(request, user_id):
    if request.method != "POST":
        messages.error(request, "Invalid request.")
        return redirect("facility_users")

    active_facility_id = request.session.get('active_facility_id')
    target_profile = get_object_or_404(UserProfile, user_id=user_id)

    if request.user.username != "craigianxx":
        if str(target_profile.facility_id) != str(active_facility_id):
            messages.error(request, "Security Exception: You cannot modify staff from a different facility.")
            return redirect("facility_users")

    target_profile.user.is_active = True
    target_profile.user.save(update_fields=["is_active"])

    create_audit_log(
        request=request,
        action="UPDATE",
        module="Account Management",
        description=f"Activated user {target_profile.user.username}",
        object_id=str(target_profile.user.id)
    )

    messages.success(request, f"Account for {target_profile.user.first_name} activated successfully.")
    return redirect("facility_users")