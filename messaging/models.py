from django.db import models
from django.conf import settings

class ChatRoom(models.Model):
    name = models.CharField(max_length=255)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='online_users', blank=True)

    def __str__(self):
        return self.name

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, related_name='messages', on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    attachment = models.FileField(upload_to='message/attachment/')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Message by {self.author.username} in {self.room.name}'

    class Meta:
        ordering = ('timestamp',)


class MessageReply(models.Model):
    message = models.ForeignKey(Message, related_name='replies', on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='replies', on_delete=models.CASCADE)
    content = models.TextField()
    attachment = models.FileField(upload_to='messages/attachments/')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Reply by {self.author.username} to message {self.message.id}'

    class Meta:
        ordering = ('timestamp',)
