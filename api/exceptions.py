from rest_framework.views import exception_handler
from rest_framework.exceptions import (
    ValidationError, 
    NotFound, 
    PermissionDenied, 
    NotAuthenticated
)

def fhir_exception_handler(exc, context):
    """
    Custom exception handler that converts standard DRF errors 
    into FHIR OperationOutcome resources.
    """
    # Call REST framework's default exception handler first to get the standard response
    response = exception_handler(exc, context)

    # If the response is None, it means it's a 500 Server Error not caught by DRF.
    # We only format the exceptions DRF knows about (4xx errors).
    if response is not None:
        
        # Set defaults
        severity = "error"
        code = "processing"
        diagnostics = str(exc)

        # Map DRF exception types to FHIR issue codes
        if isinstance(exc, ValidationError):
            code = "invalid"
            
            # Flatten DRF's validation dictionary into a readable string
            # e.g. from {"identifier": ["Required."]} to "identifier: Required."
            if isinstance(response.data, dict):
                error_messages = []
                for field, errors in response.data.items():
                    # Handle both lists of errors and single string errors
                    if isinstance(errors, list):
                        error_messages.append(f"{field}: {errors[0]}")
                    else:
                        error_messages.append(f"{field}: {errors}")
                diagnostics = "; ".join(error_messages)
                
            elif isinstance(response.data, list):
                diagnostics = "; ".join([str(e) for e in response.data])

        elif isinstance(exc, NotFound):
            code = "not-found"
            diagnostics = "The requested resource could not be found on this server."
            
        elif isinstance(exc, (NotAuthenticated, PermissionDenied)):
            code = "security"
            diagnostics = "You do not have permission to perform this action."

        # Completely replace the DRF response payload with a FHIR OperationOutcome
        response.data = {
            "resourceType": "OperationOutcome",
            "issue": [
                {
                    "severity": severity,
                    "code": code,
                    "diagnostics": diagnostics
                }
            ]
        }

    return response