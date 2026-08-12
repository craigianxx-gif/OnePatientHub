from django.contrib import admin
from .models import AccountRequest

@admin.register(AccountRequest)
class AccountRequestAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'staff_id', 'requested_role', 'status', 'created_at')
    list_filter = ('status', 'requested_role')
    search_fields = ('full_name', 'email', 'staff_id')
    readonly_fields = ('created_at',)