from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.http import JsonResponse

def custom_404(request, exception=None):
    return JsonResponse({
        "status": "error",
        "code": 404,
        "message": f"Resource not found: {request.path}",
    }, status=404)

def custom_500(request):
    return JsonResponse({
        "status": "error",
        "code": 500,
        "message": "Internal server error",
    }, status=500)

handler404 = custom_404
handler500 = custom_500

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('chatbot.urls')),
    path('api/v1/', include('bookings.urls')),
    path('api/', include('chatbot.urls')),
    path('api/', include('bookings.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

