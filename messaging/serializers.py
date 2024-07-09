from rest_framework import serializers
from accounts.serializers import UserSerializer
from .models import ChatRoom, Message, MessageReply


class MessageReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageReply
        fields = ['id', 'author', 'content', 'timestamp']

class MessageSerializer(serializers.ModelSerializer):
    replies = MessageReplySerializer(many=True, read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'room', 'author', 'content',  'attachment', 'timestamp', 'replies']

class ChatRoomSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = ChatRoom
        fields = ['id', 'name', 'participants', 'messages']
