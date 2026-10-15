from django.urls import path
from . import views

urlpatterns = [

    path(
        "create/<str:oph_id>/",
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
    
    path(
        "referrals/<int:referral_id>/status/<str:new_status>/", 
        views.update_referral_status, 
        name="update_referral_status"
    ),
    
    path(
        "<int:referral_id>/", 
        views.referral_detail, 
        name="referral_detail"
    ),

]