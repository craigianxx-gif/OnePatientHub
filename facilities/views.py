from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.core.exceptions import FieldError  # NEW: Import for safe error handling

from audit.utils import create_audit_log
from .models import Facility
from .forms import FacilityForm
from accounts.decorators import administrator_required
from patients.models import Patient
from referrals.models import Referral

User = get_user_model()


# Facility directory
@login_required
@administrator_required
def facility_directory(request):
    query = request.GET.get("q", "")
    facilities = Facility.objects.all().order_by("facility_name")

    if query:
        facilities = facilities.filter(
            Q(facility_id__icontains=query) |
            Q(facility_name__icontains=query) |
            Q(province__icontains=query) |
            Q(district__icontains=query)
        )

    return render(
        request,
        "facilities/facility_directory.html",
        {
            "facilities": facilities,
            "query": query
        }
    )


# Register facility
@login_required
@administrator_required
def register_facility(request):
    if request.method == "POST":
        form = FacilityForm(request.POST)
        
        if form.is_valid():
            facility = form.save()
            
            create_audit_log(
                request=request,
                action="CREATE",
                module="Facilities",
                description=f"Registered facility {facility.facility_name}",
                object_id=facility.facility_id
            )
            return redirect("facility_directory")
    else:
        form = FacilityForm()

    return render(
        request,
        "facilities/register_facility.html",
        {
            "form": form
        }
    )


# Facility profile
@login_required
@administrator_required
def facility_profile(request, facility_id):
    facility = get_object_or_404(Facility, facility_id=facility_id)
    
    # 1. Referrals Sent
    referrals_sent = facility.referrals_made.count()
    
    # 2. Safely count Patients (via visits to this facility, fallback to global total)
    try:
        patient_count = Patient.objects.filter(visits__facility=facility).distinct().count()
    except FieldError:
        patient_count = Patient.objects.count()
        
    # 3. Safely count Staff Accounts
    try:
        staff_count = User.objects.filter(facility=facility).count()
    except FieldError:
        try:
            # Fallback if your User model uses 'assigned_facility' instead
            staff_count = User.objects.filter(assigned_facility=facility).count()
        except FieldError:
            staff_count = 0
    
    create_audit_log(
        request=request,
        action="VIEW",
        module="Facilities",
        description=f"Viewed facility profile {facility.facility_name}",
        object_id=facility.facility_id
    )
    
    return render(
        request,
        "facilities/facility_profile.html",
        {
            "facility": facility,
            "referrals_sent": referrals_sent,
            "patient_count": patient_count,
            "staff_count": staff_count
        }
    )


# Edit facility
@login_required
@administrator_required
def edit_facility(request, facility_id):
    facility = get_object_or_404(Facility, facility_id=facility_id)

    if request.method == "POST":
        form = FacilityForm(request.POST, instance=facility)
        
        if form.is_valid():
            form.save()
            
            create_audit_log(
                request=request,
                action="UPDATE",
                module="Facilities",
                description=f"Updated facility {facility.facility_name}",
                object_id=facility.facility_id
            )
            return redirect("facility_profile", facility_id=facility.facility_id)
    else:
        form = FacilityForm(instance=facility)

    return render(
        request,
        "facilities/edit_facility.html",
        {
            "form": form,
            "facility": facility
        }
    );