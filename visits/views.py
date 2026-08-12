from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .forms import VisitForm


@login_required
def create_visit(request):

    if request.method == "POST":

        form = VisitForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect("visit_success")

    else:

        form = VisitForm()

    return render(
        request,
        "visits/create_visit.html",
        {
            "form": form
        }
    )


@login_required
def visit_success(request):

    return render(
        request,
        "visits/visit_success.html"
    )