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
from .diagnostic_views import (
    DiagnosticSessionCreateView,
    DiagnosticSessionDetailView,
    DiagnosticSessionAnswerView,
    DiagnosticSessionAssessView,
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

    # Two-Call Dynamic Diagnostic Architecture Endpoints
    path('diagnostic/sessions/', DiagnosticSessionCreateView.as_view(), name='diagnostic-session-create'),
    path('diagnostic/sessions/<str:session_id>/', DiagnosticSessionDetailView.as_view(), name='diagnostic-session-detail'),
    path('diagnostic/sessions/<str:session_id>/answers/', DiagnosticSessionAnswerView.as_view(), name='diagnostic-session-answer'),
    path('diagnostic/sessions/<str:session_id>/assess/', DiagnosticSessionAssessView.as_view(), name='diagnostic-session-assess'),
]
