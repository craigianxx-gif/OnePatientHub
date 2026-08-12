from django.urls import path

from . import views


urlpatterns = [

    path(
        "create/",
        views.create_referral,
        name="create_referral"
    ),

    path(
        "success/",
        views.referral_success,
        name="referral_success"
    ),

    path(
        "",
        views.referral_list,
        name="referral_list"
    ),

    path(
        "<int:referral_id>/status/",
        views.update_referral_status,
        name="update_referral_status"
    ),

]