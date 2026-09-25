"""
Gemini Diagnostic AI Reasoning Service for Instant Mechanic.
Consulted ONLY when structured evidence indicates an ambiguous or complex automotive case.
Passes compact structured diagnostic context and validates strict JSON responses.
Falls back reliably to deterministic rules if Gemini is unavailable, 429 rate-limited, or times out.
"""
import os
import json
import re
import logging
from typing import Dict, Any, Tuple, Optional
from django.conf import settings

logger = logging.getLogger(__name__)


def extract_json_from_ai_response(text: str) -> Optional[Dict[str, Any]]:
    """Extracts and parses JSON object from model response."""
    clean = text.strip()
    # Try markdown json block
    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', clean, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            pass

    # Try outermost braces
    match = re.search(r'\{.*\}', clean, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            pass

    return None


def validate_gemini_diagnosis(data: Any) -> Optional[Dict[str, Any]]:
    """Strictly validates required keys and format for diagnostic output."""
    if not isinstance(data, dict):
        return None

    required_keys = ["possible_issue", "reasoning", "severity", "recommended_service", "safety_warning"]
    if not all(k in data and isinstance(data[k], str) and data[k].strip() for k in required_keys):
        return None

    sev = data["severity"].lower().strip()
    if sev not in ["low", "medium", "high"]:
        sev = "medium"

    conf = data.get("confidence", "high").lower().strip()
    if conf not in ["low", "medium", "high"]:
        conf = "medium"

    return {
        "possible_issue": data["possible_issue"].strip(),
        "reasoning": data["reasoning"].strip(),
        "severity": sev,
        "confidence": conf,
        "recommended_service": data["recommended_service"].strip(),
        "safety_warning": data["safety_warning"].strip(),
    }


def call_gemini_diagnostic_reasoning(
    compact_context: Dict[str, Any],
    media_info: Optional[str] = None
) -> Tuple[Optional[Dict[str, Any]], Dict[str, Any]]:
    """
    Calls Gemini API with compact structured case context.
    Returns: (parsed_diagnosis_or_None, usage_metrics)
    usage_metrics = {
      "calls": 1,
      "input_tokens": N,
      "output_tokens": N,
      "estimated_cost": float
    }
    """
    api_key = getattr(settings, 'GEMINI_API_KEY', None) or os.environ.get('GEMINI_API_KEY', '')
    usage_stats = {
        "calls": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "estimated_cost": 0.0
    }

    if not api_key:
        logger.warning("GEMINI_API_KEY not configured. Bypassing AI reasoning.")
        return None, usage_stats

    # Build compact prompt
    context_str = json.dumps(compact_context, indent=2)
    prompt = f"""
You are an expert Master Diagnostic Technician (ASE Master Certified) assisting an automotive workshop.
Analyze the following compact structured case and resolve ambiguous or competing candidate issues:

CASE CONTEXT:
{context_str}
{f"ATTACHED MEDIA ANALYSIS: {media_info}" if media_info else ""}

INSTRUCTIONS:
1. Synthesize the operating conditions, symptoms, and candidate issues.
2. Determine the most probable root mechanical or electrical cause.
3. Keep wording conservative ("Possible", "Likely", "Needs inspection").
4. Classify severity strictly as "low", "medium", or "high".
5. Recommend a specific actionable repair or inspection service.
6. Provide a concise, clear safety warning.

Return ONLY a valid JSON object matching EXACTLY this schema:
{{
  "possible_issue": "Short descriptive title of the issue",
  "confidence": "medium|high",
  "severity": "low|medium|high",
  "reasoning": "Concise mechanical explanation correlating conditions with symptoms",
  "recommended_service": "Actionable service procedure title",
  "safety_warning": "Clear safety implication if driven without repair"
}}
"""

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)

        candidate_models = ["gemini-2.5-flash", "gemini-flash-latest", "gemini-2.5-flash-lite"]
        data = None

        for m_name in candidate_models:
            try:
                model = genai.GenerativeModel(
                    model_name=m_name,
                    generation_config={"temperature": 0.2, "response_mime_type": "application/json"}
                )
                response = model.generate_content(prompt)
                usage_stats["calls"] += 1

                # Extract token usage if available in SDK
                if hasattr(response, "usage_metadata") and response.usage_metadata:
                    in_tok = getattr(response.usage_metadata, "prompt_token_count", 0) or 0
                    out_tok = getattr(response.usage_metadata, "candidates_token_count", 0) or 0
                    usage_stats["input_tokens"] += in_tok
                    usage_stats["output_tokens"] += out_tok
                    # Estimate cost: approx $0.075 / 1M input, $0.30 / 1M output for flash
                    cost = (in_tok * 0.000000075) + (out_tok * 0.00000030)
                    usage_stats["estimated_cost"] = round(cost, 6)

                raw_text = response.text.strip()
                parsed = extract_json_from_ai_response(raw_text)
                validated = validate_gemini_diagnosis(parsed)
                if validated:
                    data = validated
                    break
            except Exception as model_err:
                logger.warning(f"Gemini model {m_name} failed: {model_err}")
                continue

        return data, usage_stats

    except Exception as e:
        logger.warning(f"Gemini API invocation error: {e}")
        return None, usage_stats
