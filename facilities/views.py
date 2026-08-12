from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib.auth.decorators import login_required

from django.db.models import Q

from audit.utils import create_audit_log

from .models import Facility

from .forms import FacilityForm

from accounts.decorators import administrator_required


# ==========================================
# FACILITY DIRECTORY
# ADMINISTRATOR ONLY
# ==========================================

@login_required
@administrator_required
def facility_directory(request):

    query = request.GET.get(
        "q",
        ""
    )

    facilities = Facility.objects.all().order_by(
        "facility_name"
    )

    if query:

        facilities = facilities.filter(

            Q(
                facility_id__icontains=query
            )

            |

            Q(
                facility_name__icontains=query
            )

            |

            Q(
                province__icontains=query
            )

            |

            Q(
                district__icontains=query
            )

        )

    return render(

        request,

        "facilities/facility_directory.html",

        {

            "facilities": facilities,

            "query": query

        }

    )


# ==========================================
# REGISTER FACILITY
# ADMINISTRATOR ONLY
# ==========================================

@login_required
@administrator_required
def register_facility(request):

    if request.method == "POST":

        form = FacilityForm(

            request.POST

        )

        if form.is_valid():

            facility = form.save()

            create_audit_log(

                request=request,

                action="CREATE",

                module="Facilities",

                description=(

                    f"Registered facility "

                    f"{facility.facility_name}"

                ),

                object_id=facility.facility_id

            )

            return redirect(

                "facility_directory"

            )

    else:

        form = FacilityForm()

    return render(

        request,

        "facilities/register_facility.html",

        {

            "form": form

        }

    )


# ==========================================
# FACILITY PROFILE
# ADMINISTRATOR ONLY
# ==========================================

@login_required
@administrator_required
def facility_profile(

    request,

    facility_id

):

    facility = get_object_or_404(

        Facility,

        facility_id=facility_id

    )

    create_audit_log(

        request=request,

        action="VIEW",

        module="Facilities",

        description=(

            f"Viewed facility profile "

            f"{facility.facility_name}"

        ),

        object_id=facility.facility_id

    )

    return render(

        request,

        "facilities/facility_profile.html",

        {

            "facility": facility

        }

    )


# ==========================================
# EDIT FACILITY
# ADMINISTRATOR ONLY
# ==========================================

@login_required
@administrator_required
def edit_facility(

    request,

    facility_id

):

    facility = get_object_or_404(

        Facility,

        facility_id=facility_id

    )

    if request.method == "POST":

        form = FacilityForm(

            request.POST,

            instance=facility

        )

        if form.is_valid():

            form.save()

            create_audit_log(

                request=request,

                action="UPDATE",

                module="Facilities",

                description=(

                    f"Updated facility "

                    f"{facility.facility_name}"

                ),

                object_id=facility.facility_id

            )

            return redirect(

                "facility_profile",

                facility_id=facility.facility_id

            )

    else:

        form = FacilityForm(

            instance=facility

        )

    return render(

        request,

        "facilities/edit_facility.html",

        {

            "form": form,

            "facility": facility

        }

    )