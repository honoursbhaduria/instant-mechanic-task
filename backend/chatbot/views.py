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
from .logic.validator import (
    is_greeting_only,
    is_car_related,
    extract_vehicle_info,
    get_rejection_reply,
    get_greeting_reply,
    is_security_threat,
    get_security_rejection_reply
)
from .logic.safety_rules import check_safety_critical_condition
from .logic.state_tracker import update_conversation_state, get_initial_state
from .logic.question_engine import get_next_question
from .logic.diagnostic_engine import perform_diagnosis
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
    1. Zero-Trust Security Gate (SQLi / prompt injection).
    2. Immediate Safety Hazard Gate (brake failure, fire, fuel leak).
    3. Greeting Gate.
    4. Domain Boundary Gate (reject off-topic).
    5. Deterministic Fact Extraction & Conversation State Update.
    6. Dynamic Targeted Question Generation (0 Gemini calls).
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
            conversation = Conversation.objects.create(state=get_initial_state())

        if not conversation.state or not isinstance(conversation.state, dict):
            conversation.state = get_initial_state()

        # Save user message to database
        user_msg = Message.objects.create(
            conversation=conversation,
            role='user',
            content=user_message_text if user_message_text else f"[Uploaded {media_type or 'Media'}]",
            media_type=media_type or 'text',
            media_url=media_url
        )

        # 1. Zero-Trust Security Gate: Prompt Injection / SQLi / Jailbreak
        if user_message_text and is_security_threat(user_message_text):
            reply_text = get_security_rejection_reply()
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
                "is_security_refusal": True
            }, status=status.HTTP_200_OK)

        # 2. Immediate Safety Hazard Gate
        if user_message_text:
            safety = check_safety_critical_condition(user_message_text)
            if safety["is_safety_critical"]:
                reply_text = safety["warning"] + f"\n\nRecommended Immediate Service: {safety['recommended_service']}"
                conversation.state["safety_critical"] = True
                conversation.state["diagnostic_status"] = "ready"
                conversation.save()
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
                    "can_diagnose": True,
                    "is_safety_critical": True,
                    "diagnostic_status": "ready",
                    "vehicle_info": conversation.vehicle_info,
                    "progress": {"completed": 4, "estimated_required": 4},
                    "quick_replies": ["Run Diagnosis", "Book Emergency Service"]
                }, status=status.HTTP_200_OK)

        # 3. Case: Greeting only
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
                "diagnostic_status": "collecting",
                "vehicle_info": conversation.vehicle_info,
                "progress": {"completed": 0, "estimated_required": 4},
                "quick_replies": [
                    "Hyundai Creta clicking noise when turning",
                    "Maruti Swift engine won't start",
                    "Honda City brake squealing",
                    "Engine overheating in traffic"
                ]
            }, status=status.HTTP_200_OK)

        # 4. Case: Off-topic query rejection
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
                "diagnostic_status": "collecting",
                "is_rejected": True
            }, status=status.HTTP_200_OK)

        # 5. Media handling
        if media_url:
            media_item = {"media_type": media_type or 'image', "media_url": media_url}
            conversation.state.setdefault("media", []).append(media_item)

        # 6. Fact Extraction & State Progression
        last_question_field = conversation.state.get("next_field")
        state = update_conversation_state(conversation.state, user_message_text or "", last_question_field)

        # Persist extracted facts into ConversationFact table in Neon PostgreSQL
        try:
            from .models import ConversationFact
            from .logic.state_tracker import state_to_facts_dict
            facts_dict = state_to_facts_dict(state)
            for f_key, f_val in facts_dict.items():
                if f_val is not None and not isinstance(f_val, dict) and f_val != "":
                    ConversationFact.objects.update_or_create(
                        conversation=conversation,
                        key=f_key,
                        defaults={
                            "value": f_val,
                            "confidence": 1.0,
                            "source": "user_message",
                            "message": user_msg
                        }
                    )
        except Exception:
            pass

        # Sync vehicle info on conversation model
        v_parts = [str(state["vehicle"].get(k, "")) for k in ["year", "make", "model"] if state["vehicle"].get(k)]
        if v_parts and not conversation.vehicle_info:
            conversation.vehicle_info = " ".join(v_parts)
            conversation.save(update_fields=['vehicle_info'])

        turn_count = conversation.messages.filter(role='user').count()
        state["question_count"] = turn_count

        # 7. Dynamic Targeted Question Generation
        reply_text, quick_replies, next_field, can_diagnose = get_next_question(state, turn_count, user_message_text or "")
        state["next_field"] = next_field
        conversation.state = state
        conversation.save()

        # Save assistant reply to database
        Message.objects.create(
            conversation=conversation,
            role='assistant',
            content=reply_text,
            media_type='text'
        )

        completed = len(state.get("answered_fields", []))
        estimated_required = max(completed + (0 if can_diagnose else 1), 4)

        return Response({
            "reply": reply_text,
            "conversation_id": conversation.id,
            "needs_more_info": not can_diagnose,
            "can_diagnose": can_diagnose,
            "diagnostic_status": state.get("diagnostic_status", "collecting"),
            "vehicle_info": conversation.vehicle_info,
            "progress": {
                "completed": completed,
                "estimated_required": estimated_required
            },
            "next_field": next_field,
            "quick_replies": quick_replies,
            "candidate_issues": state.get("candidate_issues", [])
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
    1. Loads structured conversation state.
    2. Checks for cached diagnosis (preventing duplicate Gemini calls).
    3. Runs deterministic rule engine & candidate scoring.
    4. Decides whether Gemini reasoning is needed (ambiguous cases) or local rule suffices.
    5. Fallback logic on Gemini failure/rate-limit.
    6. Saves structured Diagnosis record with source ('rules', 'gemini', 'fallback').
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

        # Media attachments if any
        user_messages = conversation.messages.filter(role='user')
        media_items = [
            f"Type: {m.media_type}, URL: {m.media_url}"
            for m in user_messages if m.media_url
        ]
        media_info = "; ".join(media_items) if media_items else None

        # Execute diagnostic engine
        diagnosis, is_cached = perform_diagnosis(conversation, media_info=media_info)

        # Add summary message to conversation for record keeping if newly generated
        if not is_cached:
            summary_msg = (
                f"Diagnostic Result:\n"
                f"• Issue: {diagnosis.diagnosis}\n"
                f"• Severity: {diagnosis.severity.upper()}\n"
                f"• Confidence: {diagnosis.confidence.upper()}\n"
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
            "confidence": diagnosis.confidence,
            "recommendation": diagnosis.recommendation,
            "service": diagnosis.service,
            "reasoning": diagnosis.reasoning,
            "safety_warning": diagnosis.safety_warning,
            "vehicle": diagnosis.vehicle or conversation.vehicle_info,
            "source": diagnosis.source,
            "is_cached": is_cached,
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
