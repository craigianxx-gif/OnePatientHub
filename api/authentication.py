import hashlib
from django.utils import timezone
from rest_framework import authentication
from rest_framework import exceptions
from .models import ApiKey

class SystemUser:
    """A mock user object to satisfy DRF's IsAuthenticated permission."""
    def __init__(self, system):
        self.is_authenticated = True
        self.system = system

class ExternalAPIKeyAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return None  # Let DRF handle standard session auth if no Bearer token

        raw_token = auth_header.split(' ')[1]
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

        try:
            api_key = ApiKey.objects.get(key_hash=token_hash, is_active=True)
            
            # Check expiration
            if api_key.expires_at and api_key.expires_at < timezone.now():
                raise exceptions.AuthenticationFailed('API Key has expired.')
                
            # Update last used timestamp for the dashboard
            api_key.last_used = timezone.now()
            api_key.save(update_fields=['last_used'])
            
        except ApiKey.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid or inactive API Key.')

        # Return a tuple of (user, auth) as required by DRF
        return (SystemUser(api_key.system), api_key)