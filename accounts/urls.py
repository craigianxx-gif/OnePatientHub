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


    # ==========================================
    # APPROVE ACCOUNT REQUEST
    # ==========================================

    path(
        "account-requests/<int:request_id>/approve/",
        views.approve_account_request,
        name="approve_account_request"
    ),


    # ==========================================
    # DENY ACCOUNT REQUEST
    # ==========================================

    path(
        "account-requests/<int:request_id>/deny/",
        views.deny_account_request,
        name="deny_account_request"
    ),

]