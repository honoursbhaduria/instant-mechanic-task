"""
Two-Call Dynamic Diagnostic Architecture API Views.
Endpoints:
- POST /api/v1/diagnostic/sessions/            (Gemini Call #1: Interview Planning)
- POST /api/v1/diagnostic/sessions/{id}/answers/ (Store answer, return next question, 0 Gemini calls)
- POST /api/v1/diagnostic/sessions/{id}/assess/  (Gemini Call #2: Final Assessment)
- GET  /api/v1/diagnostic/sessions/{id}/        (Restore state, returns ONLY active question)

Zero hardcoded automotive logic. Unified API response envelope.
"""
import logging
from rest_framework.views import APIView
from rest_framework import status
from django.conf import settings

from .models import DiagnosticSession, DiagnosticAnswer, AIUsageLog, Conversation, Message, Diagnosis
from .api_helpers import api_success, api_error
from .logic.gemini_interview_planner import GeminiInterviewPlanner
from .logic.gemini_diagnostic_assessor import GeminiDiagnosticAssessor
from .logic.validator import is_greeting_only, is_security_threat, get_security_rejection_reply, get_greeting_reply
from .logic.fact_extractor import detect_vehicle
from .logic.conversation_intent import analyze_answer_intent, extract_evidence_facts

logger = logging.getLogger(__name__)


class DiagnosticSessionCreateView(APIView):
    """
    POST /api/v1/diagnostic/sessions/
    Start a diagnostic session for an incident.
    Triggers Gemini Call #1 to dynamically generate an interview plan.
    Stores the full plan on the backend, but returns ONLY the first question.
    """

    def post(self, request):
        user_message = request.data.get("message", "").strip()
        vehicle_id = request.data.get("vehicle_id", "")
        vehicle_data = request.data.get("vehicle", {})

        if not user_message:
            return api_error("MISSING_MESSAGE", "The 'message' field is required and cannot be empty.", status_code=status.HTTP_400_BAD_REQUEST)

        # Zero-Trust Security Gate
        if is_security_threat(user_message):
            return api_error("SECURITY_ALERT", get_security_rejection_reply(), status_code=status.HTTP_400_BAD_REQUEST)

        # Greeting-only gate (0 Gemini calls)
        if is_greeting_only(user_message):
            return api_success({
                "session": {
                    "id": None,
                    "status": "awaiting_incident"
                },
                "progress": {
                    "answered": 0,
                    "total": 0,
                    "percentage": 0
                },
                "message": {
                    "id": "msg_greeting",
                    "role": "assistant",
                    "type": "greeting",
                    "content": (
                        "Hello! I am your Instant Mechanic senior automotive diagnostic technician.\n\n"
                        "Please describe what your vehicle is experiencing—such as collision or body damage, "
                        "strange sounds, warning lights, or breakdown conditions. Once you describe what happened, "
                        "I will conduct a step-by-step diagnostic assessment."
                    )
                },
                "question": None
            })

        # Derive vehicle context dynamically from message or input
        vehicle_context = {
            "make": None,
            "model": None,
            "year": None
        }
        if isinstance(vehicle_data, dict):
            vehicle_context.update({k: v for k, v in vehicle_data.items() if k in vehicle_context and v})

        # Extract make/model/year from user message if missing
        extracted_veh = detect_vehicle(user_message)
        if extracted_veh.get("make") and not vehicle_context["make"]:
            vehicle_context["make"] = extracted_veh["make"]
        if extracted_veh.get("model") and not vehicle_context["model"]:
            vehicle_context["model"] = extracted_veh["model"]
        if extracted_veh.get("year") and not vehicle_context["year"]:
            vehicle_context["year"] = extracted_veh["year"]

        # Call Gemini #1: Dynamic Interview Planner
        planner = GeminiInterviewPlanner()
        max_questions = getattr(settings, 'MAX_DIAGNOSTIC_QUESTIONS', 7)
        interview_plan, usage = planner.plan_interview(
            vehicle_context=vehicle_context,
            incident_message=user_message,
            question_limit=max_questions
        )

        if not interview_plan or not interview_plan.get("questions"):
            return api_error(
                "PLANNING_FAILED",
                "Unable to generate diagnostic interview plan at this time. Please retry.",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        # Create DiagnosticSession
        session = DiagnosticSession.objects.create(
            vehicle_id=vehicle_id or "",
            vehicle_info=vehicle_context,
            original_message=user_message,
            case_context={
                "case_summary": interview_plan.get("case_summary", {}),
                "known_facts": interview_plan.get("case_summary", {}).get("known_facts", []),
                "additional_facts": []
            },
            interview_plan=interview_plan,
            current_question_index=0,
            status='collecting_answers',
            gemini_calls=usage.get("calls", 1)
        )

        # Instrument token usage
        try:
            AIUsageLog.objects.create(
                session=session,
                operation='interview_planning',
                model=usage.get("model", "gemini-2.5-flash"),
                prompt_tokens=usage.get("input_tokens", 0),
                candidate_tokens=usage.get("output_tokens", 0),
                total_tokens=usage.get("total_tokens", 0),
                latency_ms=usage.get("latency_ms", 0),
                status=usage.get("status", "success")
            )
        except Exception as e:
            logger.warning(f"Failed to log AIUsageLog: {e}")

        # Link Conversation for booking and history backwards-compatibility
        try:
            veh_parts = [str(v) for v in vehicle_context.values() if v]
            conv = Conversation.objects.create(
                session_id=session.id,
                vehicle_info=" ".join(veh_parts) if veh_parts else "Vehicle",
                gemini_calls=session.gemini_calls
            )
            session.conversation = conv
            session.save(update_fields=['conversation'])
            Message.objects.create(conversation=conv, role='user', content=user_message)
        except Exception as e:
            logger.warning(f"Failed to create linked conversation: {e}")

        # Return ONLY the first question
        public_q = session.get_public_question()
        public_msg = session.get_public_message()
        progress = session.get_progress()

        if session.conversation and public_msg:
            Message.objects.create(conversation=session.conversation, role='assistant', content=public_msg["content"])

        return api_success({
            "session": {
                "id": session.id,
                "status": session.status
            },
            "progress": progress,
            "message": public_msg,
            "question": public_q
        }, status_code=status.HTTP_201_CREATED)


class DiagnosticSessionAnswerView(APIView):
    """
    POST /api/v1/diagnostic/sessions/{session_id}/answers/
    Accepts an answer to the currently active question.
    Validates question_id and session status.
    Handles user side-questions (drivability/repair) and confusion without consuming questions.
    Extracts multiple facts from single answers and preserves evidence.
    Advances progress and returns ONLY the next question (or ready_for_assessment).
    ZERO GEMINI CALLS.
    """

    def post(self, request, session_id):
        try:
            session = DiagnosticSession.objects.get(id=session_id)
        except DiagnosticSession.DoesNotExist:
            return api_error("SESSION_NOT_FOUND", f"Diagnostic session '{session_id}' not found.", status_code=status.HTTP_404_NOT_FOUND)

        if session.status == 'completed':
            return api_error("SESSION_COMPLETED", "This diagnostic session has already been completed.", status_code=status.HTTP_400_BAD_REQUEST)

        if session.status != 'collecting_answers':
            return api_error("INVALID_SESSION_STATE", f"Session is in state '{session.status}', cannot accept answers.", status_code=status.HTTP_400_BAD_REQUEST)

        question_id = request.data.get("question_id", "").strip()
        raw_answer = request.data.get("answer")

        current_q = session.get_current_question_internal()
        if not current_q:
            return api_error("NO_ACTIVE_QUESTION", "No active question found for this session.", status_code=status.HTTP_400_BAD_REQUEST)

        if question_id and question_id not in (current_q.get("id"), "active"):
            return api_error("INVALID_QUESTION", "This question is no longer active.", details={
                "expected_question_id": current_q.get("id"),
                "received_question_id": question_id
            }, status_code=status.HTTP_400_BAD_REQUEST)

        # Extract answer text preserving user natural language
        if isinstance(raw_answer, dict):
            answer_text = str(raw_answer.get("text", "")).strip()
            answer_payload = raw_answer
        else:
            answer_text = str(raw_answer or "").strip()
            answer_payload = {"text": answer_text}

        if not answer_text:
            return api_error("EMPTY_ANSWER", "Answer cannot be empty.", status_code=status.HTTP_400_BAD_REQUEST)

        # Analyze conversational intent without calling Gemini
        intent = analyze_answer_intent(answer_text)

        # 1. User expresses confusion / process skepticism
        if intent["is_confusion"]:
            clarification = (
                "You're right — I don't have enough information yet. So far I only have your initial description, "
                "and I cannot assess damage without inspecting specific components. That's why I need you to answer "
                "a few quick questions so I can give you an accurate assessment."
            )
            reprompt = f"{clarification}\n\n{current_q['question']}"
            if session.conversation:
                Message.objects.create(conversation=session.conversation, role='user', content=answer_text)
                Message.objects.create(conversation=session.conversation, role='assistant', content=reprompt)

            return api_success({
                "session": {
                    "id": session.id,
                    "status": session.status
                },
                "progress": session.get_progress(),
                "message": {
                    "id": f"msg_{session.current_question_index + 1:03d}",
                    "role": "assistant",
                    "type": "diagnostic_question",
                    "content": reprompt
                },
                "question": session.get_public_question()
            })

        # 2. User asks a drivability or repair inquiry without answering the active question
        if intent.get("is_pure_side_inquiry") or ((intent["is_drivability"] or intent["is_repair_inquiry"]) and not intent.get("has_damage_description")):
            safety_advice = (
                "A damaged bumper or body panel can sometimes be cosmetic, but if it is loose, dragging, "
                "blocking a wheel or headlight, exposing sharp parts, or masking hidden radiator/sensor damage, "
                "driving may be unsafe. Before deciding whether it is safe to drive or determining repair steps, "
                "I need to understand the physical damage first."
            )
            reprompt = f"{safety_advice}\n\n{current_q['question']}"

            # Preserve user question in case_context additional_facts
            case_ctx = session.case_context or {}
            add_facts = case_ctx.setdefault("additional_facts", [])
            add_facts.append({
                "key": "user_inquiry",
                "value": answer_text,
                "confidence": "explicit",
                "source": "user"
            })
            session.case_context = case_ctx
            session.save(update_fields=['case_context', 'updated_at'])

            if session.conversation:
                Message.objects.create(conversation=session.conversation, role='user', content=answer_text)
                Message.objects.create(conversation=session.conversation, role='assistant', content=reprompt)

            return api_success({
                "session": {
                    "id": session.id,
                    "status": session.status
                },
                "progress": session.get_progress(),
                "message": {
                    "id": f"msg_{session.current_question_index + 1:03d}",
                    "role": "assistant",
                    "type": "diagnostic_question",
                    "content": reprompt
                },
                "question": session.get_public_question()
            })

        # 3. Substantive Answer: Store answer and extract facts
        DiagnosticAnswer.objects.create(
            session=session,
            question_id=current_q["id"],
            question_text=current_q.get("question", ""),
            answer=answer_payload,
            order=session.current_question_index
        )

        # Multi-fact extraction & correction handling
        extracted_facts = extract_evidence_facts(answer_text)
        case_ctx = session.case_context or {}
        known_facts = case_ctx.setdefault("known_facts", [])
        if intent["is_correction"]:
            for kf in known_facts:
                kf["superseded"] = True
            for ef in extracted_facts:
                ef["source"] = "user_correction"
                known_facts.append(ef)
        else:
            known_facts.extend(extracted_facts)
        session.case_context = case_ctx

        if session.conversation:
            Message.objects.create(conversation=session.conversation, role='user', content=answer_text)

        # Advance question index
        session.current_question_index += 1
        total_questions = session.get_total_questions()

        if session.current_question_index < total_questions:
            # More questions remain -> return next question
            session.save(update_fields=['current_question_index', 'case_context', 'updated_at'])
            next_q = session.get_public_question()
            next_msg = session.get_public_message()
            progress = session.get_progress()

            if session.conversation and next_msg:
                Message.objects.create(conversation=session.conversation, role='assistant', content=next_msg["content"])

            return api_success({
                "session": {
                    "id": session.id,
                    "status": session.status
                },
                "progress": progress,
                "message": next_msg,
                "question": next_q
            })
        else:
            # All generated questions answered -> transition to ready_for_assessment
            session.status = 'ready_for_assessment'
            session.save(update_fields=['current_question_index', 'status', 'case_context', 'updated_at'])
            progress = session.get_progress()

            ready_msg = {
                "id": f"msg_{total_questions + 1:03d}",
                "role": "assistant",
                "type": "assessment_ready",
                "content": "Thanks. I have collected all necessary diagnostic details about your incident."
            }

            if session.conversation:
                Message.objects.create(conversation=session.conversation, role='assistant', content=ready_msg["content"])

            return api_success({
                "session": {
                    "id": session.id,
                    "status": session.status
                },
                "progress": progress,
                "message": ready_msg,
                "question": None
            })


class DiagnosticSessionAssessView(APIView):
    """
    POST /api/v1/diagnostic/sessions/{session_id}/assess/
    Triggers Gemini Call #2 to produce the final diagnostic assessment.
    Grounds all conclusions strictly in user-reported evidence.
    Idempotent: if already completed, returns existing assessment without re-calling Gemini.
    """

    def post(self, request, session_id):
        try:
            session = DiagnosticSession.objects.get(id=session_id)
        except DiagnosticSession.DoesNotExist:
            return api_error("SESSION_NOT_FOUND", f"Diagnostic session '{session_id}' not found.", status_code=status.HTTP_404_NOT_FOUND)

        # Idempotency check: if already completed, return cached assessment
        if session.status == 'completed' and session.assessment:
            return api_success({
                "session": {
                    "id": session.id,
                    "status": "completed"
                },
                "assessment": session.assessment
            })

        if session.status != 'ready_for_assessment':
            return api_error(
                "INTERVIEW_INCOMPLETE",
                f"Diagnostic interview is in state '{session.status}'. All generated interview questions must be answered before requesting final assessment.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # Transition to assessing
        session.status = 'assessing'
        session.save(update_fields=['status', 'updated_at'])

        # Compile interview transcript
        transcript = []
        for ans in session.answers.order_by('order', 'created_at'):
            ans_data = ans.answer
            ans_str = ans_data.get("text", str(ans_data)) if isinstance(ans_data, dict) else str(ans_data)
            transcript.append({
                "question": ans.question_text,
                "answer": ans_str
            })

        # Call Gemini #2: Diagnostic Assessor
        assessor = GeminiDiagnosticAssessor()
        assessment, usage = assessor.assess_case(
            vehicle_context=session.vehicle_info or {},
            original_message=session.original_message,
            interview_transcript=transcript,
            case_summary=session.case_context.get("case_summary")
        )

        session.assessment = assessment
        session.status = 'completed'
        session.gemini_calls += usage.get("calls", 1)
        session.save(update_fields=['assessment', 'status', 'gemini_calls', 'updated_at'])

        # Log AIUsageLog
        try:
            AIUsageLog.objects.create(
                session=session,
                conversation=session.conversation,
                operation='final_assessment',
                model=usage.get("model", "gemini-2.5-flash"),
                prompt_tokens=usage.get("input_tokens", 0),
                candidate_tokens=usage.get("output_tokens", 0),
                total_tokens=usage.get("total_tokens", 0),
                latency_ms=usage.get("latency_ms", 0),
                status=usage.get("status", "success")
            )
        except Exception as e:
            logger.warning(f"Failed to log assessment AIUsageLog: {e}")

        # Create linked Diagnosis model for booking and history
        try:
            if session.conversation:
                actions = assessment.get("recommended_actions", ["Automotive Diagnostic Inspection"])
                first_action = actions[0] if actions else "Automotive Diagnostic Inspection"
                concerns = assessment.get("possible_concerns", [])
                first_concern = concerns[0].get("title", "Vehicle Incident Assessment") if concerns else "Vehicle Incident Assessment"
                sev = assessment.get("severity", "caution")
                diag_sev = "high" if sev in ["high", "critical", "unsafe"] else ("medium" if sev in ["medium", "caution"] else "low")
                safety_msg = assessment.get("safety", {}).get("message", "")

                diag = Diagnosis.objects.create(
                    conversation=session.conversation,
                    symptoms=session.original_message[:250],
                    diagnosis=first_concern,
                    severity=diag_sev,
                    confidence="high",
                    recommendation=first_action,
                    service=first_action,
                    reasoning=assessment.get("summary", ""),
                    safety_warning=safety_msg,
                    vehicle=" ".join([str(v) for v in session.vehicle_info.values() if v]) if isinstance(session.vehicle_info, dict) else "",
                    source="gemini"
                )
                session.diagnosis = diag
                session.save(update_fields=['diagnosis'])
                Message.objects.create(
                    conversation=session.conversation,
                    role='assistant',
                    content=f"Assessment Complete: {assessment.get('summary', '')}"
                )
        except Exception as e:
            logger.warning(f"Failed to sync Diagnosis model: {e}")

        return api_success({
            "session": {
                "id": session.id,
                "status": session.status
            },
            "assessment": assessment
        })


class DiagnosticSessionDetailView(APIView):
    """
    GET /api/v1/diagnostic/sessions/{session_id}/
    Restores interrupted diagnostic state.
    Returns ONLY the currently active question or assessment if completed.
    NEVER returns the full question list.
    """

    def get(self, request, session_id):
        try:
            session = DiagnosticSession.objects.get(id=session_id)
        except DiagnosticSession.DoesNotExist:
            return api_error("SESSION_NOT_FOUND", f"Diagnostic session '{session_id}' not found.", status_code=status.HTTP_404_NOT_FOUND)

        progress = session.get_progress()

        if session.status == 'completed':
            return api_success({
                "session": {
                    "id": session.id,
                    "status": "completed"
                },
                "progress": progress,
                "assessment": session.assessment
            })

        if session.status == 'ready_for_assessment':
            return api_success({
                "session": {
                    "id": session.id,
                    "status": "ready_for_assessment"
                },
                "progress": progress,
                "message": {
                    "role": "assistant",
                    "type": "assessment_ready",
                    "content": "Thanks. I have the information I need to assess the incident."
                },
                "question": None
            })

        # collecting_answers
        public_q = session.get_public_question()
        public_msg = session.get_public_message()

        return api_success({
            "session": {
                "id": session.id,
                "status": session.status
            },
            "progress": progress,
            "message": public_msg,
            "question": public_q
        })
