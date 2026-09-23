from django.db import models
import uuid

class Conversation(models.Model):
    session_id = models.CharField(max_length=100, default=uuid.uuid4, db_index=True)
    vehicle_info = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Conversation #{self.id} ({self.session_id})"


class Message(models.Model):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    )
    MEDIA_CHOICES = (
        ('text', 'Text'),
        ('image', 'Image'),
        ('audio', 'Audio'),
        ('video', 'Video'),
    )

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    media_type = models.CharField(max_length=20, choices=MEDIA_CHOICES, blank=True, null=True, default='text')
    media_url = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"[{self.role}] Conv #{self.conversation_id}: {self.content[:30]}"


class Diagnosis(models.Model):
    SEVERITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    )

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='diagnoses')
    symptoms = models.TextField()
    diagnosis = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='medium')
    recommendation = models.TextField()
    service = models.CharField(max_length=255)
    reasoning = models.TextField(blank=True, default='')
    safety_warning = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Diagnosis #{self.id} for Conv #{self.conversation_id}: {self.service} ({self.severity})"


class UploadedMedia(models.Model):
    MEDIA_CHOICES = (
        ('image', 'Image'),
        ('audio', 'Audio'),
        ('video', 'Video'),
    )
    file = models.FileField(upload_to='uploads/%Y/%m/%d/')
    media_type = models.CharField(max_length=20, choices=MEDIA_CHOICES)
    file_name = models.CharField(max_length=255, blank=True)
    file_size = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Upload #{self.id} ({self.media_type}) - {self.file_name}"
