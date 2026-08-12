from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import AuditLog

@login_required
def audit_trail_view(request):
    query = request.GET.get("q", "").strip().upper()
    module_filter = request.GET.get("module", "").strip()

    logs = AuditLog.objects.all().order_by("-timestamp")

    if query:
        # Map common terms to standard CRUD actions if needed
        action_mapping = {
            "ADD": "CREATE",
            "NEW": "CREATE",
            "EDIT": "UPDATE",
            "CHANGE": "UPDATE",
            "REMOVE": "DELETE",
            "DEL": "DELETE",
            "VIEW": "VIEW",
        }
        
        # Check if the search query maps to a standard CRUD keyword
        mapped_action = action_mapping.get(query, query)

        logs = logs.filter(
            Q(description__icontains=query) |
            Q(user__username__icontains=query) |
            Q(action__icontains=query) |
            Q(action__icontains=mapped_action) |
            Q(module__icontains=query) |
            Q(object_id__icontains=query)
        )

    if module_filter:
        logs = logs.filter(module=module_filter)

    # Fetch distinct modules for the dropdown filter
    modules = AuditLog.objects.values_list("module", flat=True).distinct()

    return render(
        request,
        "audit/audit_trail.html",
        {
            "logs": logs,
            "query": request.GET.get("q", ""), # Keep original casing for input retention
            "selected_module": module_filter,
            "modules": modules,
        }
    )