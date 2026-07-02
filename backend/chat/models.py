import uuid
from django.db import models

class GuestSession(models.Model):
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Guest_{self.token.hex[:8]}"

class ChatMessage(models.Model):
    SENDER_CHOICES = [
        ('user', 'Employer/Guest'),
        ('system', 'System Pipeline'),
        ('agent', 'AI Agent Workhorse'),
    ]
    
    session = models.ForeignKey(GuestSession, on_delete=models.CASCADE, related_name='messages')
    agent_id = models.CharField(max_length=50) # 'direct', 'cv', 'audit', 'bio', 'voice'
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    text = models.TextField()
    audio_url = models.URLField(max_length=500, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"[{self.agent_id}] {self.sender}: {self.text[:30]}"
