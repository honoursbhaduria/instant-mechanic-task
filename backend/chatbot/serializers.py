from rest_framework import serializers
from .models import Conversation, Message, Diagnosis, UploadedMedia


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'conversation', 'role', 'content', 'media_type', 'media_url', 'created_at']


class DiagnosisSerializer(serializers.ModelSerializer):
    conversation_id = serializers.PrimaryKeyRelatedField(
        source='conversation',
        read_only=True
    )

    class Meta:
        model = Diagnosis
        fields = [
            'id',
            'conversation',
            'conversation_id',
            'symptoms',
            'diagnosis',
            'severity',
            'recommendation',
            'service',
            'reasoning',
            'safety_warning',
            'created_at'
        ]


class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    diagnoses = DiagnosisSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = [
            'id',
            'session_id',
            'vehicle_info',
            'messages',
            'diagnoses',
            'created_at',
            'updated_at'
        ]


class UploadedMediaSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = UploadedMedia
        fields = ['id', 'file', 'file_url', 'media_type', 'file_name', 'file_size', 'created_at']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and hasattr(obj.file, 'url'):
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return ""
