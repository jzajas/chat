from django.db import models
from django.conf import settings
from django.utils import timezone


class Message(models.Model):
    room = models.ForeignKey('chat.Room', on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['room', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"
    
    def to_json(self):
        return {
            'id': self.id,
            'sender': self.sender.username,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'room_id': self.room.id,
            'room_name': self.room.name,
        }