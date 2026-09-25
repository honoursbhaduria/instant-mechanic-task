"""
Unified API Response Envelope helpers for Instant Mechanic.
Consistent format across all diagnostic endpoints:
Success:
{
  "success": true,
  "data": { ... },
  "error": null
}

Error:
{
  "success": false,
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": {}
  }
}
"""
from typing import Any, Optional, Dict
from rest_framework.response import Response
from rest_framework import status


def api_success(data: Any, status_code: int = status.HTTP_200_OK) -> Response:
    """Returns a unified success response envelope."""
    return Response({
        "success": True,
        "data": data,
        "error": None
    }, status=status_code)


def api_error(
    code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    status_code: int = status.HTTP_400_BAD_REQUEST
) -> Response:
    """Returns a unified error response envelope."""
    return Response({
        "success": False,
        "data": None,
        "error": {
            "code": code,
            "message": message,
            "details": details or {}
        }
    }, status=status_code)
