from functools import wraps

from django.shortcuts import redirect
from django.contrib import messages


def administrator_required(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        # User must be logged in
        if not request.user.is_authenticated:

            return redirect("login")

        # Check whether the user has a profile
        try:

            profile = request.user.profile

        except Exception:

            messages.error(
                request,
                "Your account does not have a user profile."
            )

            return redirect("dashboard")

        # Check administrator role
        if profile.role != "administrator":

            messages.error(
                request,
                "Administrator access required."
            )

            return redirect("dashboard")

        return view_func(
            request,
            *args,
            **kwargs
        )

    return wrapper