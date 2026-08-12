from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .forms import HIVTestForm
from .models import HIVTest


@login_required
def create_hiv_test(request):

    if request.method == "POST":

        form = HIVTestForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect(
                "hiv_test_success"
            )

    else:

        form = HIVTestForm()

    return render(
        request,
        "hiv_testing/create_hiv_test.html",
        {
            "form": form
        }
    )


@login_required
def hiv_test_success(request):

    return render(
        request,
        "hiv_testing/hiv_test_success.html"
    )


@login_required
def hiv_test_list(request):

    query = request.GET.get(
        "q",
        ""
    )

    hiv_tests = HIVTest.objects.all().order_by(
        "-created_at"
    )

    if query:

        hiv_tests = hiv_tests.filter(

            Q(patient__oph_id__icontains=query) |

            Q(patient__first_name__icontains=query) |

            Q(patient__last_name__icontains=query) |

            Q(requesting_facility__icontains=query) |

            Q(result__icontains=query)

        )

    return render(
        request,
        "hiv_testing/hiv_test_list.html",
        {
            "hiv_tests": hiv_tests,
            "query": query
        }
    )


@login_required
def hiv_test_receipt(request, test_id):

    hiv_test = get_object_or_404(
        HIVTest,
        id=test_id
    )

    return render(
        request,
        "hiv_testing/hiv_test_receipt.html",
        {
            "hiv_test": hiv_test
        }
    )