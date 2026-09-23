from django.urls import path
from .views import (
    ChatView,
    UploadView,
    DiagnosisView,
    ConversationListView,
    ConversationDetailView,
    VehicleMakesView,
    VehicleModelsView,
    HealthCheckView
)

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('chat/', ChatView.as_view(), name='chat'),
    path('upload/', UploadView.as_view(), name='upload'),
    path('diagnosis/', DiagnosisView.as_view(), name='diagnosis'),
    path('conversations/', ConversationListView.as_view(), name='conversation-list'),
    path('conversations/<int:pk>/', ConversationDetailView.as_view(), name='conversation-detail'),
    path('vehicles/makes/', VehicleMakesView.as_view(), name='vehicle-makes'),
    path('vehicles/models/', VehicleModelsView.as_view(), name='vehicle-models'),
]
