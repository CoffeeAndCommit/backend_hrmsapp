from django.contrib import admin
from .models import Leave

@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = ('employee', 'leave_type', 'from_date', 'to_date', 'status', 'created_at')
    list_filter = ('status', 'leave_type', 'created_at')
    search_fields = ('employee__first_name', 'employee__email', 'reason')
    date_hierarchy = 'from_date'
