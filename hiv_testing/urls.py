from django.urls import path

from . import views


urlpatterns = [

    path(
        "",
        views.hiv_test_list,
        name="hiv_test_list"
    ),

    path(
        "create/",
        views.create_hiv_test,
        name="create_hiv_test"
    ),

    path(
        "success/",
        views.hiv_test_success,
        name="hiv_test_success"
    ),

    path(
        "receipt/<int:test_id>/",
        views.hiv_test_receipt,
        name="hiv_test_receipt"
    ),

]