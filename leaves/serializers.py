from rest_framework import serializers
from .models import Leave

class LeaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leave
        fields = [
            'id', 'from_date', 'to_date', 'no_of_days', 'reason', 
            'leave_type', 'status', 'day_status', 'late_reason', 
            'doc_link', 'rejection_reason', 'created_at'
        ]
        read_only_fields = ['status', 'rejection_reason', 'created_at']

class LeaveCalculationSerializer(serializers.Serializer):
    """
    Serializer to validate input for calculate-days API
    """
    start_date = serializers.DateField()
    end_date = serializers.DateField()
