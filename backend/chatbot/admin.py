from django.contrib import admin
from .models import Conversation, Message, Diagnosis, UploadedMedia

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'session_id', 'vehicle_info', 'created_at', 'updated_at')
    search_fields = ('session_id', 'vehicle_info')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'role', 'media_type', 'created_at')
    list_filter = ('role', 'media_type')
    search_fields = ('content',)

@admin.register(Diagnosis)
class DiagnosisAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'service', 'severity', 'created_at')
    list_filter = ('severity',)
    search_fields = ('symptoms', 'diagnosis', 'service')

@admin.register(UploadedMedia)
class UploadedMediaAdmin(admin.ModelAdmin):
    list_display = ('id', 'media_type', 'file_name', 'file_size', 'created_at')
    list_filter = ('media_type',)
