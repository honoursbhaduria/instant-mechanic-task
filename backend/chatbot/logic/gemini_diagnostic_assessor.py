"""
Gemini Diagnostic Assessor (Call #2 of Two-Call Diagnostic Architecture).
Synthesizes the complete diagnostic interview evidence and produces a final structured
assessment based ONLY on user-reported facts. ZERO hallucinated or hardcoded symptoms.
"""
import os
import json
import re
import time
import logging
from typing import Dict, Any, List, Tuple, Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class GeminiDiagnosticAssessor:
    """
    Dedicated Gemini assessor that performs Call #2: Final Diagnostic Assessment
    from the complete interview plan and user answers.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or getattr(settings, 'GEMINI_API_KEY', '') or os.environ.get('GEMINI_API_KEY', '')

    def assess_case(
        self,
        vehicle_context: Dict[str, Any],
        original_message: str,
        interview_transcript: List[Dict[str, Any]],
        case_summary: Optional[Dict[str, Any]] = None
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Executes Gemini Call #2 to produce the final diagnostic assessment.
        Returns:
          - assessment: structured assessment dictionary
          - usage_metrics: dict with calls, input_tokens, output_tokens, latency_ms, status
        """
        usage_metrics = {
            "calls": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "latency_ms": 0,
            "status": "success",
            "model": "gemini-2.5-flash"
        }

        prompt = self._construct_assessment_prompt(
            vehicle_context,
            original_message,
            interview_transcript,
            case_summary
        )

        start_time = time.time()
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)

            candidate_models = ["gemini-2.5-flash", "gemini-flash-latest", "gemini-2.5-flash-lite"]
            assessment_data = None

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
                    validated = self._validate_assessment(parsed)
                    if validated:
                        assessment_data = validated
                        break
                except Exception as model_err:
                    logger.warning(f"Gemini assessor model {m_name} failed: {model_err}")
                    continue

            latency = int((time.time() - start_time) * 1000)
            usage_metrics["latency_ms"] = latency

            if assessment_data:
                return assessment_data, usage_metrics

            logger.warning("Gemini assessment returned invalid structure; generating fallback assessment.")
            usage_metrics["status"] = "fallback"
            fallback_assessment = self._generate_fallback_assessment(original_message, interview_transcript)
            return fallback_assessment, usage_metrics

        except Exception as e:
            logger.error(f"GeminiDiagnosticAssessor encountered error: {e}")
            usage_metrics["status"] = "error"
            usage_metrics["latency_ms"] = int((time.time() - start_time) * 1000)
            fallback_assessment = self._generate_fallback_assessment(original_message, interview_transcript)
            return fallback_assessment, usage_metrics

    def _construct_assessment_prompt(
        self,
        vehicle_context: Dict[str, Any],
        original_message: str,
        interview_transcript: List[Dict[str, Any]],
        case_summary: Optional[Dict[str, Any]]
    ) -> str:
        veh_str = json.dumps(vehicle_context, indent=2)
        qa_lines = []
        for idx, item in enumerate(interview_transcript):
            q_text = item.get("question", "")
            a_text = item.get("answer", "")
            qa_lines.append(f"Q{idx+1}: {q_text}\nAnswer: {a_text}")
        interview_str = "\n\n".join(qa_lines)

        return f"""You are a master automotive diagnostic engineer and vehicle safety assessor.
A diagnostic interview has been completed for the following vehicle:

Vehicle Information:
{veh_str}

Initial Incident Reported by User:
\"{original_message}\"

Diagnostic Interview Questions & User's Answers:
{interview_str}

YOUR TASK:
Provide a rigorous, safety-oriented diagnostic assessment based EXCLUSIVELY on the evidence provided above.

CRITICAL RULES:
1. Ground every conclusion in the user's reported answers.
2. DO NOT hallucinate unrelated automotive failures (e.g. do not invent wheel bearing, coolant, or spark plug issues unless directly reported or physically caused by the event).
3. Clearly state whether physical inspection is required before further highway or high-speed driving.
4. Provide structured, actionable next steps.
5. Return ONLY a valid JSON object matching EXACTLY this schema:

{{
  "summary": "Clear, objective summary of the assessment based on user evidence",
  "severity": "low|medium|high|caution|critical",
  "possible_concerns": [
    {{
      "title": "Title of potential concern or damage",
      "confidence": "low|medium|high",
      "evidence": [
        "Specific statement or fact reported by user"
      ]
    }}
  ],
  "recommended_actions": [
    "Actionable, prioritized maintenance, inspection, or repair recommendation"
  ],
  "safety": {{
    "level": "safe|caution|unsafe|critical",
    "message": "Immediate driving safety guidance and operational warning"
  }},
  "limitations": [
    "Specific limitations of remote assessment (e.g., physical inspection required for underlying structural integrity)"
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

    def _validate_assessment(self, data: Any) -> Optional[Dict[str, Any]]:
        if not isinstance(data, dict):
            return None

        summary = str(data.get("summary", "")).strip()
        if not summary:
            return None

        severity = str(data.get("severity", "caution")).lower().strip()
        if severity not in ["low", "medium", "high", "caution", "critical"]:
            severity = "caution"

        raw_concerns = data.get("possible_concerns", [])
        valid_concerns = []
        if isinstance(raw_concerns, list):
            for c in raw_concerns:
                if isinstance(c, dict) and c.get("title"):
                    ev = c.get("evidence", [])
                    ev_list = [str(x) for x in ev] if isinstance(ev, list) else [str(ev)]
                    valid_concerns.append({
                        "title": str(c["title"]).strip(),
                        "confidence": str(c.get("confidence", "medium")).lower().strip(),
                        "evidence": ev_list
                    })

        raw_actions = data.get("recommended_actions", [])
        valid_actions = [str(a).strip() for a in raw_actions if str(a).strip()] if isinstance(raw_actions, list) else []
        if not valid_actions:
            valid_actions = ["Have the vehicle physically inspected by a certified automotive technician."]

        safety = data.get("safety", {})
        if not isinstance(safety, dict):
            safety = {
                "level": severity,
                "message": "Proceed with caution and arrange for a professional vehicle inspection."
            }
        else:
            safety = {
                "level": str(safety.get("level", severity)).lower().strip(),
                "message": str(safety.get("message", "Inspect vehicle before regular high-speed operation.")).strip()
            }

        raw_limits = data.get("limitations", [])
        valid_limits = [str(l).strip() for l in raw_limits if str(l).strip()] if isinstance(raw_limits, list) else [
            "A physical inspection is required to verify internal and structural vehicle integrity."
        ]

        return {
            "summary": summary,
            "severity": severity,
            "possible_concerns": valid_concerns,
            "recommended_actions": valid_actions,
            "safety": safety,
            "limitations": valid_limits
        }

    def _generate_fallback_assessment(
        self,
        original_message: str,
        interview_transcript: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        evidence_items = []
        for item in interview_transcript:
            ans = item.get("answer", "").strip()
            if ans:
                evidence_items.append(f"{item.get('question', '')}: {ans}")

        return {
            "summary": f"Reported incident: '{original_message}'. Based on the user responses, an immediate inspection is recommended.",
            "severity": "caution",
            "possible_concerns": [
                {
                    "title": "Incident Damage or Component Malfunction",
                    "confidence": "medium",
                    "evidence": evidence_items[:3] or [original_message]
                }
            ],
            "recommended_actions": [
                "Schedule a professional vehicle inspection.",
                "Monitor for fluid leaks, strange noises, or changes in driving dynamics."
            ],
            "safety": {
                "level": "caution",
                "message": "Exercise caution when operating the vehicle and stop driving immediately if warning lights illuminate or handling feels compromised."
            },
            "limitations": [
                "Visual and mechanical inspection on a hoist is required to rule out hidden internal component damage."
            ]
        }
