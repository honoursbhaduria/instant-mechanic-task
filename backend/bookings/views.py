from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Booking
from .serializers import BookingSerializer


class BookingCreateListView(APIView):
    """
    POST /api/booking/ - Create a new booking
    GET  /api/booking/ - List recent bookings
    """
    def post(self, request):
        serializer = BookingSerializer(data=request.data)
        if serializer.is_valid():
            booking = serializer.save()
            return Response(BookingSerializer(booking).data, status=status.HTTP_201_CREATED)
        return Response(
            {
                "error": True,
                "message": "Validation failed for booking.",
                "details": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def get(self, request):
        bookings = Booking.objects.select_related('diagnosis')[:50]
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BookingDetailView(APIView):
    """
    GET /api/booking/<id>/ - Retrieve details of a booking
    """
    def get(self, request, pk):
        try:
            booking = Booking.objects.select_related('diagnosis').get(pk=pk)
        except Booking.DoesNotExist:
            return Response(
                {"error": True, "message": f"Booking #{pk} not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = BookingSerializer(booking)
        return Response(serializer.data, status=status.HTTP_200_OK)
