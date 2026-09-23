from django.urls import path
from .views import BookingCreateListView, BookingDetailView

urlpatterns = [
    path('booking/', BookingCreateListView.as_view(), name='booking-create-list'),
    path('booking/<int:pk>/', BookingDetailView.as_view(), name='booking-detail'),
]
