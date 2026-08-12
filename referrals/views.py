from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .forms import ReferralForm
from .models import Referral


@login_required
def create_referral(request):

    if request.method == "POST":

        form = ReferralForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect("referral_success")

    else:

        form = ReferralForm()

    return render(
        request,
        "referrals/create_referral.html",
        {
            "form": form
        }
    )


@login_required
def referral_success(request):

    return render(
        request,
        "referrals/referral_success.html"
    )


@login_required
def referral_list(request):

    query = request.GET.get("q", "")

    referrals = Referral.objects.all().order_by(
        "-created_at"
    )

    if query:

        referrals = referrals.filter(

            Q(patient__oph_id__icontains=query) |

            Q(patient__first_name__icontains=query) |

            Q(patient__last_name__icontains=query) |

            Q(referring_facility__icontains=query) |

            Q(receiving_facility__icontains=query)

        )

    return render(
        request,
        "referrals/referral_list.html",
        {
            "referrals": referrals,
            "query": query
        }
    )


@login_required
def update_referral_status(request, referral_id):

    referral = get_object_or_404(
        Referral,
        id=referral_id
    )

    if request.method == "POST":

        new_status = request.POST.get(
            "status"
        )

        valid_statuses = dict(
            Referral.STATUS_CHOICES
        )

        if new_status in valid_statuses:

            referral.status = new_status

            referral.save()

    return redirect(
        "referral_list"
    )