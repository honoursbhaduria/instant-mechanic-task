from django.db import models
import uuid
from typing import Optional, Dict, Any, List

class Conversation(models.Model):
    session_id = models.CharField(max_length=100, default=uuid.uuid4, db_index=True)
    vehicle_info = models.CharField(max_length=255, blank=True, default='')
    state = models.JSONField(default=dict, blank=True)
    gemini_calls = models.PositiveIntegerField(default=0)
    input_tokens = models.PositiveIntegerField(default=0)
    output_tokens = models.PositiveIntegerField(default=0)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=4, default=0.0)
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
    SOURCE_CHOICES = (
        ('rules', 'Rules Engine'),
        ('gemini', 'Gemini AI'),
        ('fallback', 'Fallback Engine'),
    )

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='diagnoses')
    symptoms = models.TextField()
    diagnosis = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='medium')
    confidence = models.CharField(max_length=20, default='medium')
    recommendation = models.TextField()
    service = models.CharField(max_length=255)
    reasoning = models.TextField(blank=True, default='')
    safety_warning = models.TextField(blank=True, default='')
    vehicle = models.CharField(max_length=255, blank=True, default='')
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='rules')
    fingerprint = models.CharField(max_length=64, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Diagnosis #{self.id} for Conv #{self.conversation_id}: {self.service} ({self.severity}) [{self.source}]"


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


# ==============================================================================
# DATA-DRIVEN DIAGNOSTIC KNOWLEDGE MODELS (Stored in Neon PostgreSQL)
# ==============================================================================

class VehicleSystem(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, default='')
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Symptom(models.Model):
    system = models.ForeignKey(VehicleSystem, on_delete=models.SET_NULL, null=True, blank=True, related_name='symptoms')
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, default='')
    aliases = models.JSONField(default=list, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.slug})"


class DiagnosticQuestion(models.Model):
    key = models.CharField(max_length=100, unique=True)
    question_text = models.TextField()
    answer_type = models.CharField(max_length=30, default='single_choice')
    category = models.CharField(max_length=100, blank=True, default='')
    priority = models.PositiveIntegerField(default=50)
    safety_critical = models.BooleanField(default=False)
    relevance_rule = models.JSONField(default=dict, blank=True)
    target_fact_key = models.CharField(max_length=100, blank=True, default='')
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-priority', 'id']

    def __str__(self):
        return f"[{self.key}] {self.question_text[:50]}"


class DiagnosticOption(models.Model):
    question = models.ForeignKey(DiagnosticQuestion, on_delete=models.CASCADE, related_name='options')
    value = models.CharField(max_length=100)
    label = models.CharField(max_length=200)
    aliases = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.question.key} -> {self.label} ({self.value})"


class DiagnosticIssue(models.Model):
    SEVERITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    )
    system = models.ForeignKey(VehicleSystem, on_delete=models.SET_NULL, null=True, blank=True, related_name='issues')
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, default='')
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='medium')
    service = models.CharField(max_length=255)
    recommendation = models.TextField(blank=True, default='')
    safety_warning = models.TextField(blank=True, default='')
    reasoning_template = models.TextField(blank=True, default='')
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.slug})"


class DiagnosticCriterion(models.Model):
    POLARITY_CHOICES = (
        ('positive', 'Positive Evidence'),
        ('negative', 'Negative Evidence'),
    )
    issue = models.ForeignKey(DiagnosticIssue, on_delete=models.CASCADE, related_name='criteria')
    field = models.CharField(max_length=100)
    operator = models.CharField(max_length=30, default='equals')
    expected_value = models.JSONField(default=dict)
    weight = models.FloatField(default=1.0)
    polarity = models.CharField(max_length=20, choices=POLARITY_CHOICES, default='positive')
    description = models.CharField(max_length=255, blank=True, default='')

    class Meta:
        ordering = ['-weight', 'id']

    def __str__(self):
        return f"{self.issue.slug}: {self.field} {self.operator} {self.expected_value} (wt: {self.weight})"


class ConversationFact(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='facts')
    key = models.CharField(max_length=100, db_index=True)
    value = models.JSONField()
    confidence = models.FloatField(default=1.0)
    source = models.CharField(max_length=50, default='user_message')
    message = models.ForeignKey(Message, on_delete=models.SET_NULL, null=True, blank=True, related_name='extracted_facts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Fact #{self.id} for Conv #{self.conversation_id}: {self.key}={self.value}"


def generate_diag_session_id():
    return f"diag_{uuid.uuid4().hex[:8]}"


class DiagnosticSession(models.Model):
    STATUS_CHOICES = (
        ('planning', 'Planning'),
        ('collecting_answers', 'Collecting Answers'),
        ('ready_for_assessment', 'Ready for Assessment'),
        ('assessing', 'Assessing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )

    id = models.CharField(max_length=64, primary_key=True, default=generate_diag_session_id)
    conversation = models.ForeignKey(Conversation, on_delete=models.SET_NULL, null=True, blank=True, related_name='diagnostic_sessions')
    diagnosis = models.ForeignKey(Diagnosis, on_delete=models.SET_NULL, null=True, blank=True, related_name='diagnostic_sessions')
    vehicle_id = models.CharField(max_length=100, blank=True, default='')
    vehicle_info = models.JSONField(default=dict, blank=True)
    original_message = models.TextField()
    case_context = models.JSONField(default=dict, blank=True)
    interview_plan = models.JSONField(default=dict, blank=True)
    current_question_index = models.PositiveIntegerField(default=0)
    assessment = models.JSONField(default=dict, blank=True)
    gemini_calls = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='planning')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"DiagnosticSession {self.id} [{self.status}]"

    def get_total_questions(self) -> int:
        questions = self.interview_plan.get("questions", [])
        return len(questions) if isinstance(questions, list) else 0

    def get_current_question_internal(self) -> Optional[dict]:
        questions = self.interview_plan.get("questions", [])
        if isinstance(questions, list) and 0 <= self.current_question_index < len(questions):
            return questions[self.current_question_index]
        return None

    def get_public_question(self) -> Optional[dict]:
        q = self.get_current_question_internal()
        if not q:
            return None
        options = []
        for i, opt in enumerate(q.get("options", [])):
            if isinstance(opt, dict):
                options.append({
                    "id": str(opt.get("id", f"opt_{i+1}")),
                    "label": str(opt.get("label", opt.get("id", "")))
                })
            else:
                options.append({
                    "id": f"opt_{i+1}",
                    "label": str(opt)
                })
        return {
            "id": q["id"],
            "answer_type": q.get("answer_type", "text"),
            "options": options
        }

    def get_public_message(self) -> Optional[dict]:
        q = self.get_current_question_internal()
        if not q:
            return None
        return {
            "id": f"msg_{self.current_question_index + 1:03d}",
            "role": "assistant",
            "type": "diagnostic_question",
            "content": q["question"]
        }

    def get_progress(self) -> dict:
        total = self.get_total_questions()
        answered = min(self.current_question_index, total)
        pct = int(round((answered / total) * 100)) if total > 0 else 0
        return {
            "answered": answered,
            "total": total,
            "percentage": pct
        }


class DiagnosticAnswer(models.Model):
    session = models.ForeignKey(DiagnosticSession, on_delete=models.CASCADE, related_name='answers')
    question_id = models.CharField(max_length=100)
    question_text = models.TextField(blank=True, default='')
    answer = models.JSONField(default=dict)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"Answer to {self.question_id} in {self.session_id}"


class AIUsageLog(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, null=True, blank=True, related_name='ai_logs')
    session = models.ForeignKey(DiagnosticSession, on_delete=models.CASCADE, null=True, blank=True, related_name='ai_logs')
    diagnosis = models.ForeignKey(Diagnosis, on_delete=models.SET_NULL, null=True, blank=True, related_name='ai_logs')
    operation = models.CharField(max_length=50, default='interview_planning')
    model = models.CharField(max_length=100, default='gemini-2.5-flash')
    prompt_tokens = models.PositiveIntegerField(default=0)
    candidate_tokens = models.PositiveIntegerField(default=0)
    total_tokens = models.PositiveIntegerField(default=0)
    latency_ms = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=30, default='success')
    error = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"AIUsage #{self.id} ({self.operation}) - {self.total_tokens} tokens"
