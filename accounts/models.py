from django.db import models
from django.conf import settings


# ==========================================
# ACCOUNT REQUEST
# ==========================================

class AccountRequest(models.Model):

    ROLE_CHOICES = (

        ("nurse", "Nurse"),

        ("administrator", "Administrator"),

    )


    STATUS_CHOICES = (

        ("pending", "Pending"),

        ("approved", "Approved"),

        ("denied", "Denied"),

    )


    full_name = models.CharField(

        max_length=150

    )


    email = models.EmailField(

        unique=True,

        help_text=(

            "Personal or institutional email."

        )

    )


    phone_number = models.CharField(

        max_length=20

    )


    staff_id = models.CharField(

        max_length=50,

        help_text=(

            "MOHCC or Facility Employee ID"

        )

    )


    requested_role = models.CharField(

        max_length=20,

        choices=ROLE_CHOICES

    )


    status = models.CharField(

        max_length=20,

        choices=STATUS_CHOICES,

        default="pending"

    )


    created_at = models.DateTimeField(

        auto_now_add=True

    )


    def __str__(self):

        return (

            f"{self.full_name} "

            f"({self.staff_id}) - "

            f"{self.get_status_display()}"

        )


# ==========================================
# USER PROFILE
# ==========================================

class UserProfile(models.Model):


    ROLE_CHOICES = (

        (

            "administrator",

            "Administrator"

        ),

        (

            "nurse",

            "Nurse"

        ),

    )


    user = models.OneToOneField(

        settings.AUTH_USER_MODEL,

        on_delete=models.CASCADE,

        related_name="profile"

    )


    role = models.CharField(

        max_length=30,

        choices=ROLE_CHOICES,

        default="nurse"

    )


    country_code = models.CharField(

        max_length=2,

        default="ZW"

    )


    staff_id = models.CharField(

        max_length=50,

        blank=True,

        null=True

    )


    phone_number = models.CharField(

        max_length=20,

        blank=True,

        null=True

    )


    # ======================================
    # FORCE TEMPORARY PASSWORD CHANGE
    # ======================================

    must_change_password = models.BooleanField(

        default=False

    )


    created_at = models.DateTimeField(

        auto_now_add=True

    )


    def __str__(self):

        return (

            f"{self.user.username} - "

            f"{self.get_role_display()}"

        )