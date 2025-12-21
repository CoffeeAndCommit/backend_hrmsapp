from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Leave(models.Model):
    class LeaveType(models.TextChoices):
        CASUAL_LEAVE = 'Casual Leave', _('Casual Leave')
        SICK_LEAVE = 'Sick Leave', _('Sick Leave')
        EARNED_LEAVE = 'Earned Leave', _('Earned Leave')
        UNPAID_LEAVE = 'Unpaid Leave', _('Unpaid Leave')
        MATERNITY_LEAVE = 'Maternity Leave', _('Maternity Leave')
        PATERNITY_LEAVE = 'Paternity Leave', _('Paternity Leave')
        OTHER = 'Other', _('Other')

    class Status(models.TextChoices):
        PENDING = 'Pending', _('Pending')
        APPROVED = 'Approved', _('Approved')
        REJECTED = 'Rejected', _('Rejected')
        CANCELLED = 'Cancelled', _('Cancelled')

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='leaves'
    )
    leave_type = models.CharField(
        max_length=50,
        choices=LeaveType.choices,
        default=LeaveType.CASUAL_LEAVE
    )
    from_date = models.DateField()
    to_date = models.DateField()
    no_of_days = models.DecimalField(max_digits=5, decimal_places=1, default=1.0)
    reason = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    day_status = models.CharField(max_length=50, blank=True, null=True, help_text="e.g. First Half, Second Half")
    late_reason = models.TextField(blank=True, null=True)
    doc_link = models.FileField(upload_to='leave_docs/', blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    rh_dates = models.JSONField(default=list, blank=True, help_text="List of Restricted Holiday dates")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee} - {self.leave_type} ({self.from_date} to {self.to_date})"
