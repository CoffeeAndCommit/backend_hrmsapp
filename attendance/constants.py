"""
Constants for attendance app - date/time formats and other constants
"""
from django.conf import settings

# Date/Time Format Constants
DATE_FORMAT = getattr(settings, 'ATTENDANCE_DATE_FORMAT', '%Y-%m-%d')
TIME_12HR_FORMAT = getattr(settings, 'ATTENDANCE_TIME_12HR_FORMAT', '%I:%M %p')
DATETIME_ISO_FORMAT = getattr(settings, 'ATTENDANCE_DATETIME_ISO_FORMAT', '%Y-%m-%dT%H:%M:%SZ')
DAY_NAME_FORMAT = getattr(settings, 'ATTENDANCE_DAY_NAME_FORMAT', '%A')
DAY_NUMBER_FORMAT = getattr(settings, 'ATTENDANCE_DAY_NUMBER_FORMAT', '%d')
ADMIN_ALERT_MESSAGE_MISSING_TIME = "In/Out Time Missing"

