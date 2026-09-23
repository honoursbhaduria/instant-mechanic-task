"""
Chatbot views implementing:
- POST /api/chat/
- POST /api/upload/
- POST /api/diagnosis/
- GET  /api/conversations/
- GET  /api/conversations/<id>/
- GET  /api/vehicles/makes/
- GET  /api/vehicles/models/
- GET  /api/health/
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
import os
import mimetypes

from .models import Conversation, Message, Diagnosis, UploadedMedia
from .serializers import ConversationSerializer, MessageSerializer, DiagnosisSerializer, UploadedMediaSerializer
from .logic.validator import is_greeting_only, is_car_related, extract_vehicle_info, get_rejection_reply, get_greeting_reply
from .logic.state_tracker import analyze_conversation_state, generate_followup_question
from .logic.gemini_service import diagnose_with_gemini
from .logic.vehicle_service import COMMON_MAKES, fetch_models_from_nhtsa

# Max upload limit: 25MB
MAX_UPLOAD_SIZE = 25 * 1024 * 1024

SUPPORTED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
SUPPORTED_AUDIO_EXTENSIONS = {'.mp3', '.wav', '.ogg', '.m4a', '.webm', '.aac'}
SUPPORTED_VIDEO_EXTENSIONS = {'.mp4', '.webm', '.mov', '.mkv'}


class HealthCheckView(APIView):
    def get(self, request):
        return Response({
            "status": "healthy",
            "service": "Instant Mechanic AI API",
            "version": "1.0.0"
        })


class ChatView(APIView):
    """
    POST /api/chat/
    Validates query using traditional backend logic:
    1. Rejects off-topic queries politely
    2. Handles greetings politely
    3. Checks missing information and asks follow-ups
    4. Triggers diagnosis readiness when sufficient info is gathered
    """
    def post(self, request):
        conversation_id = request.data.get('conversation_id')
        user_message_text = request.data.get('message', '').strip()
        media_url = request.data.get('media_url', None)
        media_type = request.data.get('media_type', None)

        if not user_message_text and not media_url:
            return Response(
                {"error": True, "message": "Either 'message' or 'media_url' must be provided."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Retrieve or create Conversation
        if conversation_id:
            try:
                conversation = Conversation.objects.get(id=conversation_id)
            except Conversation.DoesNotExist:
                return Response(
                    {"error": True, "message": f"Conversation #{conversation_id} not found."},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            conversation = Conversation.objects.create()

        # Save user message to database
        user_msg = Message.objects.create(
            conversation=conversation,
            role='user',
            content=user_message_text if user_message_text else f"[Uploaded {media_type or 'Media'}]",
            media_type=media_type or 'text',
            media_url=media_url
        )

        # Detect vehicle info if present and update conversation
        if user_message_text:
            detected_vehicle = extract_vehicle_info(user_message_text)
            if detected_vehicle and not conversation.vehicle_info:
                conversation.vehicle_info = detected_vehicle
                conversation.save(update_fields=['vehicle_info'])

        # Case 1: Greeting only
        if user_message_text and is_greeting_only(user_message_text):
            reply_text = get_greeting_reply()
            Message.objects.create(
                conversation=conversation,
                role='assistant',
                content=reply_text,
                media_type='text'
            )
            return Response({
                "reply": reply_text,
                "conversation_id": conversation.id,
                "needs_more_info": True,
                "can_diagnose": False,
                "vehicle_info": conversation.vehicle_info
            }, status=status.HTTP_200_OK)

        # Case 2: Check if car/mechanical related
        # If this is the first message or conversation has no car context yet
        has_prior_car_context = any(
            is_car_related(m.content) for m in conversation.messages.filter(role='user')
        )

        if not has_prior_car_context and user_message_text and not is_car_related(user_message_text):
            reply_text = get_rejection_reply()
            Message.objects.create(
                conversation=conversation,
                role='assistant',
                content=reply_text,
                media_type='text'
            )
            return Response({
                "reply": reply_text,
                "conversation_id": conversation.id,
                "needs_more_info": False,
                "can_diagnose": False,
                "is_rejected": True
            }, status=status.HTTP_200_OK)

        # Case 3: Vehicle/symptom state tracking & follow-up logic
        state = analyze_conversation_state(conversation.messages.all(), conversation.vehicle_info)
        reply_text, needs_more_info = generate_followup_question(state, user_message_text or "")

        # Save assistant reply to database
        Message.objects.create(
            conversation=conversation,
            role='assistant',
            content=reply_text,
            media_type='text'
        )

        return Response({
            "reply": reply_text,
            "conversation_id": conversation.id,
            "needs_more_info": needs_more_info,
            "can_diagnose": not needs_more_info,
            "vehicle_info": state["vehicle"] or conversation.vehicle_info
        }, status=status.HTTP_200_OK)


class UploadView(APIView):
    """
    POST /api/upload/
    Accepts image, audio, or video files.
    Enforces 25MB max limit (413) and supported types (415).
    """
    def post(self, request):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response(
                {"error": True, "message": "No file uploaded. Key 'file' is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 413 File too large
        if file_obj.size > MAX_UPLOAD_SIZE:
            return Response(
                {"error": True, "message": "File too large. Maximum allowed size is 25MB."},
                status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
            )

        # Detect media type from extension and content_type
        ext = os.path.splitext(file_obj.name)[1].lower()
        content_type = file_obj.content_type or mimetypes.guess_type(file_obj.name)[0] or ""

        if ext in SUPPORTED_IMAGE_EXTENSIONS or content_type.startswith('image/'):
            media_type = 'image'
        elif ext in SUPPORTED_AUDIO_EXTENSIONS or content_type.startswith('audio/'):
            media_type = 'audio'
        elif ext in SUPPORTED_VIDEO_EXTENSIONS or content_type.startswith('video/'):
            media_type = 'video'
        else:
            return Response(
                {"error": True, "message": f"Unsupported media type '{ext or content_type}'. Supported: images (JPEG/PNG/WEBP), audio (MP3/WAV/OGG/M4A), video (MP4/WEBM/MOV)."},
                status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
            )

        # Save uploaded file
        upload = UploadedMedia.objects.create(
            file=file_obj,
            media_type=media_type,
            file_name=file_obj.name,
            file_size=file_obj.size
        )

        file_url = request.build_absolute_uri(upload.file.url)
        return Response({
            "id": upload.id,
            "file_url": file_url,
            "media_type": media_type,
            "file_name": upload.file_name,
            "file_size": upload.file_size
        }, status=status.HTTP_201_CREATED)


class DiagnosisView(APIView):
    """
    POST /api/diagnosis/
    Calls Gemini AI ONLY when diagnosis reasoning is needed.
    Passes structured information (Vehicle, Symptoms, Conditions, Media)
    and stores structured diagnosis in SQLite.
    """
    def post(self, request):
        conversation_id = request.data.get('conversation_id')
        if not conversation_id:
            return Response(
                {"error": True, "message": "'conversation_id' is required for diagnosis."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            return Response(
                {"error": True, "message": f"Conversation #{conversation_id} not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Gather structured information from conversation history
        user_messages = conversation.messages.filter(role='user')
        all_user_text = " ".join([m.content for m in user_messages])

        # Media attachments if any
        media_items = [
            f"Type: {m.media_type}, URL: {m.media_url}"
            for m in user_messages if m.media_url
        ]
        media_info = "; ".join(media_items) if media_items else "None"

        vehicle = conversation.vehicle_info
        if not vehicle:
            # Try to extract again from full text
            vehicle = extract_vehicle_info(all_user_text)

        symptoms = all_user_text
        conditions = "Reported during driving/operation"

        # Execute Gemini reasoning diagnosis (with rule-based fallback)
        ai_result = diagnose_with_gemini(
            vehicle=vehicle,
            symptoms=symptoms,
            conditions=conditions,
            media_info=media_info
        )

        # Save Diagnosis record in database
        diagnosis = Diagnosis.objects.create(
            conversation=conversation,
            symptoms=symptoms[:500],
            diagnosis=ai_result.get("possible_issue", "Mechanical Issue"),
            severity=ai_result.get("severity", "medium"),
            recommendation=ai_result.get("recommended_service", "Vehicle Inspection"),
            service=ai_result.get("recommended_service", "Vehicle Inspection"),
            reasoning=ai_result.get("reasoning", ""),
            safety_warning=ai_result.get("safety_warning", "")
        )

        # Also add summary message to conversation for record keeping
        summary_msg = (
            f"🔍 Diagnostic Result:\n"
            f"• Issue: {diagnosis.diagnosis}\n"
            f"• Severity: {diagnosis.severity.upper()}\n"
            f"• Recommended Service: {diagnosis.service}\n\n"
            f"{diagnosis.reasoning}"
        )
        Message.objects.create(
            conversation=conversation,
            role='assistant',
            content=summary_msg,
            media_type='text'
        )

        return Response({
            "id": diagnosis.id,
            "conversation_id": conversation.id,
            "diagnosis": diagnosis.diagnosis,
            "severity": diagnosis.severity,
            "recommendation": diagnosis.recommendation,
            "service": diagnosis.service,
            "reasoning": diagnosis.reasoning,
            "safety_warning": diagnosis.safety_warning,
            "vehicle": vehicle,
            "created_at": diagnosis.created_at
        }, status=status.HTTP_200_OK)


class ConversationListView(APIView):
    """GET /api/conversations/ - list all conversations"""
    def get(self, request):
        conversations = Conversation.objects.prefetch_related('messages', 'diagnoses')[:50]
        serializer = ConversationSerializer(conversations, many=True)
        return Response(serializer.data)


class ConversationDetailView(APIView):
    """GET /api/conversations/<id>/ - get full conversation details"""
    def get(self, request, pk):
        try:
            conversation = Conversation.objects.prefetch_related('messages', 'diagnoses').get(pk=pk)
        except Conversation.DoesNotExist:
            return Response(
                {"error": True, "message": f"Conversation #{pk} not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = ConversationSerializer(conversation)
        return Response(serializer.data)


class VehicleMakesView(APIView):
    """GET /api/vehicles/makes/ - return list of popular makes + full access"""
    def get(self, request):
        return Response({
            "makes": sorted(COMMON_MAKES)
        })


class VehicleModelsView(APIView):
    """GET /api/vehicles/models/?make=hyundai - return all models for make from NHTSA API"""
    def get(self, request):
        make = request.query_params.get('make', '').strip()
        if not make:
            return Response(
                {"error": True, "message": "Query parameter 'make' is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        models = fetch_models_from_nhtsa(make)
        return Response({
            "make": make,
            "count": len(models),
            "models": models
        })
