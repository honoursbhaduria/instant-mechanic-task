from rest_framework import serializers
from .models import Booking
from chatbot.models import Diagnosis
from chatbot.serializers import DiagnosisSerializer
import re


class BookingSerializer(serializers.ModelSerializer):
    diagnosis_id = serializers.PrimaryKeyRelatedField(
        queryset=Diagnosis.objects.all(),
        source='diagnosis',
        required=False,
        allow_null=True
    )
    diagnosis_details = DiagnosisSerializer(source='diagnosis', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id',
            'diagnosis_id',
            'diagnosis_details',
            'customer_name',
            'phone',
            'vehicle',
            'preferred_date',
            'preferred_time',
            'service',
            'status',
            'notes',
            'created_at'
        ]

    def validate_customer_name(self, value):
        val = value.strip()
        if len(val) < 2:
            raise serializers.ValidationError("Customer name must be at least 2 characters.")
        return val

    def validate_phone(self, value):
        # Clean non-digit characters to verify digits
        digits = re.sub(r'\D', '', value)
        if len(digits) < 10:
            raise serializers.ValidationError("Please provide a valid phone number with at least 10 digits.")
        return value.strip()

    def validate_vehicle(self, value):
        val = value.strip()
        if not val:
            raise serializers.ValidationError("Vehicle information is required.")
        return val

    def validate_service(self, value):
        val = value.strip()
        if not val:
            raise serializers.ValidationError("Service type is required.")
        return val
