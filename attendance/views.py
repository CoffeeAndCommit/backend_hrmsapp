from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from django.db import transaction
from datetime import datetime
from calendar import monthrange

# Optional django-filter import
try:
    from django_filters.rest_framework import DjangoFilterBackend
    HAS_DJANGO_FILTER = True
except ImportError:
    HAS_DJANGO_FILTER = False

from .models import Attendance
from .serializers import (
    AttendanceListSerializer,
    AttendanceDetailSerializer,
    AttendanceCreateUpdateSerializer,
    CheckInSerializer,
    CheckOutSerializer,
    MonthlyAttendanceSerializer
)
from holidays.models import Holiday
from employees.models import Employee
from .services import AttendanceCalculationService
from django.conf import settings
from .constants import DATE_FORMAT, TIME_12HR_FORMAT


class AttendanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Attendance management
    
    list: Get all attendance records (filtered by permissions)
    retrieve: Get single attendance details
    create: Create attendance record (Admin only)
    update: Update attendance (Admin only)
    destroy: Delete attendance (Admin only)
    """
    queryset = Attendance.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    if HAS_DJANGO_FILTER:
        filter_backends.insert(0, DjangoFilterBackend)
    filterset_fields = [
        'employee', 'date', 'day_type', 'admin_alert'
    ] if HAS_DJANGO_FILTER else []
    search_fields = [
        'employee__first_name', 'employee__last_name', 
        'employee__employee_id', 'date'
    ]
    ordering_fields = ['date', 'in_time', 'out_time', 'created_at']
    ordering = ['-date']
    
    def get_serializer_class(self):
        """Use different serializers based on action"""
        if self.action == 'list':
            return AttendanceListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return AttendanceCreateUpdateSerializer
        return AttendanceDetailSerializer
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # Admin/Staff can see all attendance
        if user.is_staff:
            return queryset
        
        # Regular users can only see their own attendance
        if hasattr(user, 'employee_profile'):
            return queryset.filter(employee=user.employee_profile)
        
        return queryset.none()
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]
    
    def perform_create(self, serializer):
        """Set created_by and determine day_type when creating attendance"""
        attendance = serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user
        )
        self._determine_day_type(attendance)
        attendance.save()
    
    def perform_update(self, serializer):
        """Set updated_by and recalculate when updating attendance"""
        attendance = serializer.save(updated_by=self.request.user)
        self._determine_day_type(attendance)
        attendance.save()
    
    def _determine_day_type(self, attendance):
        """Determine day_type based on date, holidays, and weekend"""
        AttendanceCalculationService.determine_day_type(attendance, today=timezone.now().date())
    
    @action(detail=False, methods=['post'], url_path='check-in')
    def check_in(self, request):
        """
        Employee check-in endpoint
        POST /api/attendance/check-in/
        Body: {"date": "2025-12-01", "notes": "Optional notes"}
        """
        user = request.user
        
        # Check if user has employee profile
        if not hasattr(user, 'employee_profile'):
            return Response({
                "error": 1,
                "message": "User must have an employee profile to check in."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        employee = user.employee_profile
        serializer = CheckInSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                "error": 1,
                "message": "Validation failed",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get date (default to today)
        check_date = serializer.validated_data.get('date', timezone.now().date())
        with transaction.atomic():
            # Lock row to prevent concurrent check-ins
            existing = Attendance.objects.select_for_update().filter(
                employee=employee,
                date=check_date
            ).first()

            if existing and existing.in_time:
                return Response({
                    "error": 1,
                    "message": f"Already checked in for {check_date}"
                }, status=status.HTTP_400_BAD_REQUEST)

            # Create or update attendance record
            if existing:
                existing.in_time = timezone.now()
                existing.day_text = serializer.validated_data.get('notes', '')
                self._determine_day_type(existing)
                existing.save()
                attendance = existing
            else:
                # Create new attendance record
                attendance = Attendance.objects.create(
                    employee=employee,
                    date=check_date,
                    in_time=timezone.now(),
                    day_text=serializer.validated_data.get('notes', ''),
                    office_working_hours=getattr(settings, 'ATTENDANCE_DEFAULT_WORKING_HOURS', '09:00'),
                    orignal_total_time=getattr(settings, 'ATTENDANCE_DEFAULT_TOTAL_TIME_SECONDS', 32400),
                    created_by=user,
                    updated_by=user
                )
                self._determine_day_type(attendance)
                attendance.save()
        
        return Response({
            "error": 0,
            "data": {
                "message": "Checked in successfully",
                "attendance_id": attendance.id,
                "check_in_time": attendance.in_time.strftime(TIME_12HR_FORMAT),
                "date": attendance.date.strftime(DATE_FORMAT)
            }
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'], url_path='check-out')
    def check_out(self, request):
        """
        Employee check-out endpoint
        POST /api/attendance/check-out/
        Body: {"date": "2025-12-01", "notes": "Optional notes"}
        """
        user = request.user
        
        # Check if user has employee profile
        if not hasattr(user, 'employee_profile'):
            return Response({
                "error": 1,
                "message": "User must have an employee profile to check out."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        employee = user.employee_profile
        serializer = CheckOutSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                "error": 1,
                "message": "Validation failed",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get date (default to today)
        check_date = serializer.validated_data.get('date', timezone.now().date())
        
        with transaction.atomic():
            attendance = Attendance.objects.select_for_update().filter(
                employee=employee,
                date=check_date
            ).first()
            
            if not attendance:
                return Response({
                    "error": 1,
                    "message": f"No check-in found for {check_date}. Please check in first."
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if attendance.out_time:
                return Response({
                    "error": 1,
                    "message": f"Already checked out for {check_date}"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Set check-out time
            attendance.out_time = timezone.now()
            if serializer.validated_data.get('notes'):
                attendance.text = serializer.validated_data.get('notes', '')
            attendance.updated_by = user
            
            # Save will trigger time calculations
            self._determine_day_type(attendance)
            attendance.save()
        
        # Format response
        from .serializers import format_seconds_to_time, format_time_to_12hr
        
        return Response({
            "error": 0,
            "data": {
                "message": "Checked out successfully",
                "attendance_id": attendance.id,
                "check_in_time": format_time_to_12hr(attendance.in_time),
                "check_out_time": format_time_to_12hr(attendance.out_time),
                "total_time": format_seconds_to_time(attendance.seconds_actual_worked_time),
                "extra_time": format_seconds_to_time(attendance.seconds_extra_time),
                "extra_time_status": attendance.extra_time_status,
                "date": attendance.date.strftime(DATE_FORMAT)
            }
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='monthly')
    def monthly_attendance(self, request):
        """
        Get monthly attendance summary
        GET /api/attendance/monthly/?month=12&year=2025&userid=838
        Returns: {error: 0, data: {...}} matching your API format
        """
        user = request.user
        
        # Get query parameters
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        userid = request.query_params.get('userid')
        
        # Validate month and year
        if not month or not year:
            return Response({
                "error": 1,
                "message": "month and year query parameters are required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            month = int(month)
            year = int(year)
            
            if month < 1 or month > 12:
                raise ValueError("Month must be between 1 and 12")
        except ValueError as e:
            return Response({
                "error": 1,
                "message": f"Invalid month or year: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get employee
        if userid:
            # Admin can view any employee's attendance
            if user.is_staff:
                try:
                    employee = Employee.objects.get(id=int(userid))
                except (Employee.DoesNotExist, ValueError):
                    return Response({
                        "error": 1,
                        "message": "Employee not found"
                    }, status=status.HTTP_404_NOT_FOUND)
            else:
                # Regular users can only view their own
                if not hasattr(user, 'employee_profile') or str(user.employee_profile.id) != str(userid):
                    return Response({
                        "error": 1,
                        "message": "You can only view your own attendance"
                    }, status=status.HTTP_403_FORBIDDEN)
                employee = user.employee_profile
        else:
            # Default to logged-in user's employee profile
            if not hasattr(user, 'employee_profile'):
                return Response({
                    "error": 1,
                    "message": "User must have an employee profile"
                }, status=status.HTTP_400_BAD_REQUEST)
            employee = user.employee_profile
        
        # Get attendance records for the month
        start_date = datetime(year, month, 1).date()
        num_days = monthrange(year, month)[1]
        end_date = datetime(year, month, num_days).date()
        
        attendance_records = Attendance.objects.filter(
            employee=employee,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date')
        
        # Get holidays for the month
        holidays_list = Holiday.objects.filter(
            date__year=year,
            date__month=month,
            is_active=True
        )
        
        # Serialize monthly data
        response_data = MonthlyAttendanceSerializer.serialize_monthly_data(
            attendance_records,
            employee,
            month,
            year,
            holidays_list
        )
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='today')
    def today(self, request):
        """
        Get today's attendance for logged-in employee
        GET /api/attendance/today/
        """
        user = request.user
        
        if not hasattr(user, 'employee_profile'):
            return Response({
                "error": 1,
                "message": "User must have an employee profile"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        employee = user.employee_profile
        today = timezone.now().date()
        
        attendance = Attendance.objects.filter(
            employee=employee,
            date=today
        ).first()
        
        if not attendance:
            return Response({
                "error": 0,
                "data": {
                    "message": "No attendance record for today",
                    "date": today.strftime(DATE_FORMAT),
                    "has_check_in": False,
                    "has_check_out": False
                }
            })
        
        serializer = AttendanceDetailSerializer(attendance)
        return Response({
            "error": 0,
            "data": serializer.data
        })
    
    @action(detail=False, methods=['get'], url_path='my-attendance')
    def my_attendance(self, request):
        """
        Get logged-in employee's attendance history
        GET /api/attendance/my-attendance/?start_date=2025-12-01&end_date=2025-12-31
        """
        user = request.user
        
        if not hasattr(user, 'employee_profile'):
            return Response({
                "error": 1,
                "message": "User must have an employee profile"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        employee = user.employee_profile
        queryset = Attendance.objects.filter(employee=employee)
        
        # Filter by date range if provided
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            try:
                start_date = datetime.strptime(start_date, DATE_FORMAT).date()
                queryset = queryset.filter(date__gte=start_date)
            except ValueError:
                return Response({
                    "error": 1,
                    "message": f"Invalid start_date format. Use {DATE_FORMAT}"
                }, status=status.HTTP_400_BAD_REQUEST)
        
        if end_date:
            try:
                end_date = datetime.strptime(end_date, DATE_FORMAT).date()
                queryset = queryset.filter(date__lte=end_date)
            except ValueError:
                return Response({
                    "error": 1,
                    "message": f"Invalid end_date format. Use {DATE_FORMAT}"
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Paginate results
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = AttendanceDetailSerializer(page, many=True)
            return self.get_paginated_response({
                "error": 0,
                "data": serializer.data
            })
        
        serializer = AttendanceDetailSerializer(queryset, many=True)
        return Response({
            "error": 0,
            "data": serializer.data
        })

