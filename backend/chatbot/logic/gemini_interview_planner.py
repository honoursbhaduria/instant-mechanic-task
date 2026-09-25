"""
Gemini Interview Planner (Call #1 of Two-Call Diagnostic Architecture).
Analyzes the initial incident message and vehicle context, and dynamically generates
a structured diagnostic interview plan (1 to MAX_DIAGNOSTIC_QUESTIONS).
ZERO automotive diagnostic logic or incident types are hardcoded.
"""
import os
import json
import re
import time
import logging
import uuid
from typing import Dict, Any, List, Tuple, Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class GeminiInterviewPlanner:
    """
    Dedicated Gemini planner that analyzes an initial vehicle incident and
    creates a tailored, non-hardcoded diagnostic interview plan.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or getattr(settings, 'GEMINI_API_KEY', '') or os.environ.get('GEMINI_API_KEY', '')

    def plan_interview(
        self,
        vehicle_context: Dict[str, Any],
        incident_message: str,
        question_limit: Optional[int] = None
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Executes Gemini Call #1 to dynamically generate the interview plan.
        Returns:
          - interview_plan: dict with case_summary and questions list
          - usage_metrics: dict with calls, input_tokens, output_tokens, latency_ms, status
        """
        if question_limit is None:
            question_limit = getattr(settings, 'MAX_DIAGNOSTIC_QUESTIONS', 7)

        usage_metrics = {
            "calls": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "latency_ms": 0,
            "status": "success",
            "model": "gemini-2.5-flash"
        }

        # Build prompt
        prompt = self._construct_planning_prompt(vehicle_context, incident_message, question_limit)

        start_time = time.time()
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)

            candidate_models = ["gemini-2.5-flash", "gemini-flash-latest", "gemini-2.5-flash-lite"]
            plan_data = None

            for m_name in candidate_models:
                try:
                    model = genai.GenerativeModel(
                        model_name=m_name,
                        generation_config={
                            "temperature": 0.2,
                            "response_mime_type": "application/json"
                        }
                    )
                    response = model.generate_content(prompt)
                    usage_metrics["calls"] = 1
                    usage_metrics["model"] = m_name

                    if hasattr(response, "usage_metadata") and response.usage_metadata:
                        in_tok = getattr(response.usage_metadata, "prompt_token_count", 0) or 0
                        out_tok = getattr(response.usage_metadata, "candidates_token_count", 0) or 0
                        usage_metrics["input_tokens"] = in_tok
                        usage_metrics["output_tokens"] = out_tok
                        usage_metrics["total_tokens"] = in_tok + out_tok

                    raw_text = response.text.strip()
                    parsed = self._extract_json(raw_text)
                    validated = self._validate_plan(parsed, question_limit)
                    if validated:
                        plan_data = validated
                        break
                except Exception as model_err:
                    logger.warning(f"Gemini planner model {m_name} failed: {model_err}")
                    continue

            latency = int((time.time() - start_time) * 1000)
            usage_metrics["latency_ms"] = latency

            if plan_data:
                return plan_data, usage_metrics

            logger.warning("Gemini planning returned invalid or empty plan")
            usage_metrics["status"] = "failed"
            return None, usage_metrics

        except Exception as e:
            logger.error(f"GeminiInterviewPlanner encountered error: {e}")
            usage_metrics["status"] = "error"
            usage_metrics["latency_ms"] = int((time.time() - start_time) * 1000)
            return None, usage_metrics

    def _construct_planning_prompt(
        self,
        vehicle_context: Dict[str, Any],
        incident_message: str,
        question_limit: int
    ) -> str:
        veh_str = json.dumps(vehicle_context, indent=2)
        return f"""You are an expert automotive diagnostic systems architect.
A user reported the following vehicle incident or problem:
\"\"\"{incident_message}\"\"\"

Vehicle Information:
{veh_str}

Your task:
Analyze the reported incident and design a targeted, dynamic diagnostic interview plan containing between 1 and {question_limit} questions.

CRITICAL INSTRUCTIONS:
1. DO NOT assume fixed incident categories (e.g. collision, mechanical, electrical, etc.). Reason directly from what the user described.
2. Formulate targeted questions that clarify missing facts, damage locations, operational symptoms, warnings, or immediate drivability concerns.
3. Order questions logically: start with fundamental impact/symptom clarification, followed by operational behavior and visual/sensor observations.
4. Do NOT generate filler questions just to reach the maximum limit. If 3 or 4 questions are sufficient, generate only 3 or 4.
5. Answer types can be "text", "single_choice", "multiple_choice", or "boolean".
6. If options are provided for choice types, keep them concise and natural.
7. Return ONLY a valid JSON object matching EXACTLY this schema:

{{
  "case_summary": {{
    "description": "Concise summary of the reported incident",
    "known_facts": [
      {{
        "key": "string identifier",
        "value": "known fact value",
        "confidence": 0.95,
        "source": "user_message"
      }}
    ]
  }},
  "questions": [
    {{
      "id": "q_1",
      "question": "Clear, direct question text",
      "purpose": "Internal technical reason for asking this question",
      "answer_type": "text|single_choice|multiple_choice|boolean",
      "options": [
        {{
          "id": "opt_1",
          "label": "Option label"
        }}
      ],
      "required": true,
      "priority": "high|medium|low"
    }}
  ]
}}"""

    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        clean = text.strip()
        match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', clean, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except Exception:
                pass
        match = re.search(r'\{.*\}', clean, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass
        return None

    def _validate_plan(self, data: Any, question_limit: int) -> Optional[Dict[str, Any]]:
        if not isinstance(data, dict):
            return None

        case_summary = data.get("case_summary", {})
        if not isinstance(case_summary, dict) or not case_summary.get("description"):
            case_summary = {
                "description": "Reported vehicle incident",
                "known_facts": []
            }

        raw_questions = data.get("questions", [])
        if not isinstance(raw_questions, list) or not raw_questions:
            return None

        validated_questions = []
        seen_ids = set()

        for idx, q in enumerate(raw_questions[:question_limit]):
            if not isinstance(q, dict):
                continue
            q_text = str(q.get("question", "")).strip()
            if not q_text:
                continue

            q_id = str(q.get("id", f"q_{idx+1}")).strip()
            if q_id in seen_ids or not q_id:
                q_id = f"q_{idx+1}_{uuid.uuid4().hex[:4]}"
            seen_ids.add(q_id)

            a_type = str(q.get("answer_type", "text")).lower().strip()
            if a_type not in ["text", "single_choice", "multiple_choice", "boolean"]:
                a_type = "text"

            raw_opts = q.get("options", [])
            valid_opts = []
            if isinstance(raw_opts, list):
                for o_idx, opt in enumerate(raw_opts):
                    if isinstance(opt, dict):
                        opt_id = str(opt.get("id", f"opt_{o_idx+1}"))
                        opt_label = str(opt.get("label", opt_id))
                        valid_opts.append({"id": opt_id, "label": opt_label})
                    elif isinstance(opt, str) and opt.strip():
                        valid_opts.append({"id": f"opt_{o_idx+1}", "label": opt.strip()})

            validated_questions.append({
                "id": q_id,
                "question": q_text,
                "purpose": str(q.get("purpose", "")).strip(),
                "answer_type": a_type,
                "options": valid_opts,
                "required": bool(q.get("required", True)),
                "priority": str(q.get("priority", "medium")).lower().strip()
            })

        if not validated_questions:
            return None

        return {
            "case_summary": case_summary,
            "questions": validated_questions
        }

