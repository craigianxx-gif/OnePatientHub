from .models import AccountRequest

def pending_account_requests(request):
    """
    Globally provides the count of pending account requests 
    for authenticated administrators.
    """
    # Check if user is logged in (you can also add your admin check here)
    if request.user.is_authenticated:
        count = AccountRequest.objects.filter(status="pending").count()
        return {"pending_requests_count": count}
    
    return {"pending_requests_count": 0}