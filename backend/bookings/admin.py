from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'phone', 'vehicle', 'service', 'preferred_date', 'preferred_time', 'status', 'created_at')
    list_filter = ('status', 'preferred_date')
    search_fields = ('customer_name', 'phone', 'vehicle', 'service')
