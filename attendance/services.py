from django.utils import timezone
from django.conf import settings


class AttendanceCalculationService:
    """Shared helpers for attendance calculations and day type logic."""

    @staticmethod
    def calculate_worked_seconds(in_time, out_time):
        """Return worked seconds; 0 if either timestamp is missing."""
        if not (in_time and out_time):
            return 0
        return int((out_time - in_time).total_seconds())

    @staticmethod
    def calculate_extra_seconds(worked_seconds, scheduled_seconds):
        """Return overtime/undertime seconds."""
        return worked_seconds - scheduled_seconds

    @staticmethod
    def extra_time_status(extra_seconds):
        """Return status marker based on extra time."""
        if extra_seconds > 0:
            return '+'
        if extra_seconds < 0:
            return '-'
        return ''

    @staticmethod
    def determine_day_type(attendance, today=None):
        """
        Determine day type based on holidays, weekends, future date, and joining date.
        Keeps logic in one place so views and model can share it.
        """
        from holidays.models import Holiday

        date = attendance.date
        today = today or timezone.now().date()

        # Before joining date
        if attendance.employee.joining_date and date < attendance.employee.joining_date:
            attendance.is_day_before_joining = True

        # Weekend
        if date.weekday() >= 5:  # 5=Saturday, 6=Sunday
            attendance.day_type = 'WEEKEND_OFF'
            return attendance.day_type

        # Holiday
        is_holiday = Holiday.objects.filter(date=date, is_active=True).exists()
        if is_holiday:
            attendance.day_type = 'HOLIDAY'
            return attendance.day_type

        # Future date - treat as working day (FUTURE_WORKING_DAY removed)
        if date > today:
            attendance.day_type = 'WORKING_DAY'
            return attendance.day_type

        # Half day vs working day
        if attendance.in_time and attendance.out_time:
            worked_seconds = AttendanceCalculationService.calculate_worked_seconds(
                attendance.in_time, attendance.out_time
            )
            half_day_threshold = getattr(settings, 'ATTENDANCE_HALF_DAY_THRESHOLD', 0.5)
            if worked_seconds < (attendance.orignal_total_time * half_day_threshold):
                attendance.day_type = 'HALF_DAY'
            else:
                attendance.day_type = 'WORKING_DAY'
        else:
            attendance.day_type = 'WORKING_DAY'

        return attendance.day_type

    @staticmethod
    def should_flag_admin_alert(attendance):
        """
        Flag missing in/out only on working days; skip alerts for holidays/weekends/leave.
        """
        if attendance.day_type in ['HOLIDAY', 'WEEKEND_OFF', 'LEAVE_DAY']:
            return False
        return not (attendance.in_time and attendance.out_time)

