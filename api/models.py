from django.db import models


class ConnectedSystem(models.Model):

    STATUS_CHOICES = [

        ("Connected", "Connected"),
        ("Disconnected", "Disconnected"),
        ("Maintenance", "Maintenance"),

    ]

    AUTH_CHOICES = [

        ("Bearer Token", "Bearer Token"),
        ("API Key", "API Key"),
        ("OAuth2", "OAuth2"),
        ("Basic Auth", "Basic Auth"),

    ]

    SYSTEM_TYPE_CHOICES = [

        ("Hospital", "Hospital"),
        ("Laboratory", "Laboratory"),
        ("Shared Health Record", "Shared Health Record"),
        ("Client Registry", "Client Registry"),
        ("DHIS2", "DHIS2"),
        ("Pharmacy", "Pharmacy"),
        ("Other", "Other"),

    ]

    system_name = models.CharField(
        max_length=200
    )

    system_type = models.CharField(
        max_length=100,
        choices=SYSTEM_TYPE_CHOICES
    )

    organization = models.CharField(
        max_length=200
    )

    fhir_version = models.CharField(
        max_length=20,
        default="R4"
    )

    base_url = models.URLField()

    authentication = models.CharField(
        max_length=50,
        choices=AUTH_CHOICES,
        default="Bearer Token"
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="Connected"
    )

    last_sync = models.DateTimeField(
        null=True,
        blank=True
    )

    description = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        ordering = [

            "system_name"

        ]

    def __str__(self):

        return self.system_name


class ApiKey(models.Model):
    system = models.ForeignKey(ConnectedSystem, on_delete=models.CASCADE, related_name='api_keys')
    name = models.CharField(max_length=150, help_text="Descriptive name (e.g., 'Harare EHR Production Key')")
    key_hash = models.CharField(max_length=64, unique=True, help_text="Secure hash of the token")
    prefix = models.CharField(max_length=10, help_text="First few characters for identification")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    last_used = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.system.system_name})"


class FhirTransaction(models.Model):
    DIRECTION_CHOICES = [
        ("Inbound", "Inbound (Received from external system)"),
        ("Outbound", "Outbound (Sent to external system)"),
    ]

    system = models.ForeignKey(ConnectedSystem, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    direction = models.CharField(max_length=20, choices=DIRECTION_CHOICES, default="Inbound")
    resource_type = models.CharField(max_length=50, help_text="e.g., Patient, Organization, Bundle")
    method = models.CharField(max_length=10, help_text="GET, POST, PUT, etc.")
    endpoint = models.CharField(max_length=255)
    status_code = models.IntegerField(help_text="HTTP status code returned")
    payload = models.TextField(help_text="Raw JSON payload sent or received")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.direction}] {self.method} {self.resource_type} ({self.status_code}) - {self.created_at.strftime('%Y-%m-%d %H:%M')}"