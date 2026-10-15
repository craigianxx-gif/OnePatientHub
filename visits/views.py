from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import VisitForm

@login_required
def create_visit(request):

    # 1. Retrieve the active facility context
    active_facility_id = request.session.get('active_facility_id')
    
    if not active_facility_id:
        messages.error(request, "Session expired or facility not selected. Please log in again.")
        return redirect("login")

    if request.method == "POST":
        form = VisitForm(request.POST)

        if form.is_valid():
            visit = form.save(commit=False)
            
            # 2. Securely inject the facility automatically
            visit.facility_id = active_facility_id
            
            # 3. Securely inject the currently logged-in user as the provider
            provider_name = request.user.get_full_name() or request.user.username
            visit.healthcare_provider = provider_name
            
            visit.save()
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