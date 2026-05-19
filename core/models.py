import uuid
from django.db import models

class TTSConversion(models.Model):
    """Model to track TTS conversions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.TextField()
    language = models.CharField(max_length=50)
    voice_id = models.CharField(max_length=100)
    speed = models.FloatField(default=1.0)
    volume = models.FloatField(default=1.0)
    audio_file = models.FileField(upload_to='audio/', null=True, blank=True)
    file_format = models.CharField(max_length=10, default='mp3')
    file_size = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.language} - {self.voice_id} - {self.created_at}"
