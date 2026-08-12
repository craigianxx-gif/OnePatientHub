from django.urls import path

from . import views


urlpatterns = [

    path(
        "",
        views.facility_directory,
        name="facility_directory"
    ),

    path(
        "register/",
        views.register_facility,
        name="register_facility"
    ),

    path(
        "<str:facility_id>/",
        views.facility_profile,
        name="facility_profile"
    ),

    path(
        "<str:facility_id>/edit/",
        views.edit_facility,
        name="edit_facility"
    ),

]