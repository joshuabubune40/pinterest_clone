from rest_framework import generics, permissions
from .models import ChatRoom, Message, MessageReply
from .serializers import ChatRoomSerializer, MessageSerializer, MessageReplySerializer

class ChatRoomListCreateView(generics.ListCreateAPIView):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]

class MessageListCreateView(generics.ListCreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class MessageReplyListCreateView(generics.ListCreateAPIView):
    queryset = MessageReply.objects.all()
    serializer_class = MessageReplySerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

