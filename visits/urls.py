from django.urls import path

from . import views


urlpatterns = [

    path(
        "create/",
        views.create_visit,
        name="create_visit"
    ),

    path(
        "success/",
        views.visit_success,
        name="visit_success"
    ),

]