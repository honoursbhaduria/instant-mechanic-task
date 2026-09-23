from django.db import models

class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    diagnosis = models.ForeignKey(
        'chatbot.Diagnosis',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bookings'
    )
    customer_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    vehicle = models.CharField(max_length=150)
    preferred_date = models.CharField(max_length=30)
    preferred_time = models.CharField(max_length=30)
    service = models.CharField(max_length=255)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='confirmed')
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Booking #{self.id} for {self.customer_name} ({self.service}) - {self.status}"
