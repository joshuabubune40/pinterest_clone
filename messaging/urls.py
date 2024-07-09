from django.urls import path
from .views import ChatRoomListCreateView, MessageListCreateView, MessageReplyListCreateView

urlpatterns = [
    path('chatrooms/', ChatRoomListCreateView.as_view(), name='chatroom-list-create'),
    path('messages/', MessageListCreateView.as_view(), name='message-list-create'),
    path('replies/', MessageReplyListCreateView.as_view(), name='message-reply-list-create'),
]