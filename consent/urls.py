from django.urls import path

from . import views


urlpatterns = [

    path(

        "",

        views.consent_list,

        name="consent_list"

    ),

    path(

        "patient/<str:oph_id>/",

        views.manage_consent,

        name="manage_consent"

    ),
    

]