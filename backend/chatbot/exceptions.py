"""
Custom exception handler for REST Framework to produce clean, consistent JSON error responses.
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        custom_data = {
            "error": True,
            "status_code": response.status_code,
            "message": "An error occurred with your request.",
            "details": response.data,
        }

        # Humanize messages based on status codes
        if response.status_code == 400:
            custom_data["message"] = "Invalid request data. Please check your inputs."
        elif response.status_code == 404:
            custom_data["message"] = "The requested resource was not found."
        elif response.status_code == 413:
            custom_data["message"] = "File too large. Maximum allowed size is 25MB."
        elif response.status_code == 415:
            custom_data["message"] = "Unsupported media type. Supported formats are images (JPEG/PNG/WEBP), audio (MP3/WAV/OGG/M4A), and video (MP4/WEBM/MOV)."
        elif response.status_code == 429:
            custom_data["message"] = "Rate limit exceeded or AI service is temporarily busy. Please wait a moment and try again."

        response.data = custom_data
        return response

    # Unhandled 500 exceptions
    logger.exception("Unhandled server exception: %s", exc)
    return Response(
        {
            "error": True,
            "status_code": 500,
            "message": "Internal server error. Please try again.",
            "details": str(exc),
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
