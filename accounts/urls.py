from django.urls import path
from . import views

urlpatterns = [

    # ==========================================
    # LOGIN
    # ==========================================
    path(
        "",
        views.login_view,
        name="login"
    ),

    # ==========================================
    # LOGOUT
    # ==========================================
    path(
        "logout/",
        views.logout_view,
        name="logout"
    ),

    # ==========================================
    # ACCOUNT REQUESTS
    # ADMINISTRATOR
    # ==========================================
    path(
        "account-requests/",
        views.account_requests,
        name="account_requests"
    ),

    path(
        "account-requests/<int:request_id>/approve/",
        views.approve_account_request,
        name="approve_account_request"
    ),

    path(
        "account-requests/<int:request_id>/deny/",
        views.deny_account_request,
        name="deny_account_request"
    ),

    # ==========================================
    # FACILITY USERS (ACTIVE STAFF)
    # ADMINISTRATOR
    # ==========================================
    path(
        "users/",
        views.facility_users,
        name="facility_users"
    ),

    path(
        "users/<int:user_id>/remove/",
        views.remove_facility_user,
        name="remove_facility_user"
    ),

    path(
        "users/<int:user_id>/deactivate/",
        views.deactivate_facility_user,
        name="deactivate_facility_user"
    ),

    path(
        "users/<int:user_id>/activate/",
        views.activate_facility_user,
        name="activate_facility_user"
    ),

    # ==========================================
    # SETTINGS
    # ==========================================
    path(
        "settings/",
        views.settings_view,
        name="settings"
    ),
    
    path(
        "settings/profile/",
        views.profile_settings,
        name="profile_settings"
    ),

    path(
        "settings/password/",
        views.password_settings,
        name="password_settings"
    ),
    
    # ==========================================
    # LEGAL & POLICIES
    # ==========================================
    path(
        "terms-of-use/",
        views.terms_of_use,
        name="terms_of_use"
    ),

    path(
        "privacy-statement/",
        views.privacy_statement,
        name="privacy_statement"
    ),

    path(
        "software-services-agreement/",
        views.software_services_agreement,
        name="software_services_agreement"
    ),

]