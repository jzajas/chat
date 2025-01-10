from django.db import models
from django.conf import settings
from django.utils import timezone


class Room(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='joined_rooms',
        through='RoomMember'
    )
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'participant_count': self.participants.count()
        }


class RoomMember(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(default=timezone.now)
    is_admin = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['room', 'user']
    
    def __str__(self):
        return f"{self.user.username} in {self.room.name}"