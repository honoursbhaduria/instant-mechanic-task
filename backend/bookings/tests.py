from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from chatbot.models import Conversation, Diagnosis
from bookings.models import Booking


class BookingAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.conv = Conversation.objects.create(vehicle_info="Hyundai Creta")
        self.diagnosis = Diagnosis.objects.create(
            conversation=self.conv,
            symptoms="Clicking noise while turning",
            diagnosis="CV Joint wear",
            severity="medium",
            recommendation="Inspect CV joint",
            service="CV Joint Inspection"
        )

    def test_create_booking_success(self):
        payload = {
            "diagnosis_id": self.diagnosis.id,
            "customer_name": "Honours",
            "phone": "9876543210",
            "vehicle": "Hyundai Creta",
            "preferred_date": "2026-09-25",
            "preferred_time": "11:00 AM",
            "service": "CV Joint Inspection",
            "notes": "Please check both front axles."
        }
        res = self.client.post('/api/booking/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['customer_name'], 'Honours')
        self.assertEqual(res.data['status'], 'confirmed')
        self.assertIn('id', res.data)

    def test_create_booking_invalid_phone_400(self):
        payload = {
            "diagnosis_id": self.diagnosis.id,
            "customer_name": "Honours",
            "phone": "123",  # Invalid short phone
            "vehicle": "Hyundai Creta",
            "preferred_date": "2026-09-25",
            "preferred_time": "11:00 AM",
            "service": "CV Joint Inspection"
        }
        res = self.client.post('/api/booking/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_booking_detail(self):
        booking = Booking.objects.create(
            diagnosis=self.diagnosis,
            customer_name="Honours",
            phone="9876543210",
            vehicle="Hyundai Creta",
            preferred_date="2026-09-25",
            preferred_time="11:00 AM",
            service="CV Joint Inspection",
            status="confirmed"
        )
        res = self.client.get(f'/api/booking/{booking.id}/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['customer_name'], "Honours")
        self.assertEqual(res.data['service'], "CV Joint Inspection")

    def test_get_booking_not_found_404(self):
        res = self.client.get('/api/booking/99999/')
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
