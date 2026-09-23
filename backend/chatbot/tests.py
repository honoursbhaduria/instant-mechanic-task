from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from .models import Conversation, Message, Diagnosis
from bookings.models import Booking


class ChatbotAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_health_check(self):
        res = self.client.get('/api/health/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['status'], 'healthy')

    def test_chat_car_query_followup(self):
        # User reports clicking noise while turning
        payload = {
            "message": "My Hyundai Creta is making a clicking noise when I turn."
        }
        res = self.client.post('/api/chat/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("conversation_id", res.data)
        self.assertIn("reply", res.data)
        # Should detect Hyundai Creta
        self.assertIn("Creta", res.data.get("vehicle_info", ""))
        self.assertTrue(res.data.get("needs_more_info"))

    def test_chat_greeting(self):
        payload = {"message": "Hello there!"}
        res = self.client.post('/api/chat/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("Instant Mechanic", res.data["reply"])

    def test_chat_off_topic_rejection(self):
        payload = {"message": "Can you give me a recipe for chocolate cake and solve my calculus homework?"}
        res = self.client.post('/api/chat/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data.get("is_rejected"))
        self.assertIn("exclusively in car diagnostics", res.data["reply"])

    def test_chat_empty_message_error(self):
        res = self.client.post('/api/chat/', {"message": ""}, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_image_success(self):
        # Create in-memory dummy image
        file_io = BytesIO()
        image = Image.new('RGB', (100, 100), color='red')
        image.save(file_io, format='JPEG')
        file_io.seek(0)
        uploaded_file = SimpleUploadedFile("engine.jpg", file_io.read(), content_type="image/jpeg")

        res = self.client.post('/api/upload/', {'file': uploaded_file}, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['media_type'], 'image')
        self.assertIn('file_url', res.data)

    def test_upload_unsupported_type_415(self):
        uploaded_file = SimpleUploadedFile("malicious.exe", b"binary content", content_type="application/octet-stream")
        res = self.client.post('/api/upload/', {'file': uploaded_file}, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_diagnosis_flow(self):
        # Create conversation with symptoms
        conv = Conversation.objects.create(vehicle_info="Hyundai Creta 2022")
        Message.objects.create(
            conversation=conv,
            role='user',
            content='Clicking noise while turning left at low speed.'
        )

        res = self.client.post('/api/diagnosis/', {"conversation_id": conv.id}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("diagnosis", res.data)
        self.assertIn("severity", res.data)
        self.assertIn("service", res.data)
        self.assertIn("recommendation", res.data)

    def test_diagnosis_not_found_404(self):
        res = self.client.post('/api/diagnosis/', {"conversation_id": 99999}, format='json')
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_vehicle_makes_endpoint(self):
        res = self.client.get('/api/vehicles/makes/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("makes", res.data)
        self.assertIn("Hyundai", res.data["makes"])
