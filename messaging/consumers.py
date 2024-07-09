import django
django.setup()
import json
import base64
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.files.base import ContentFile
from .models import ChatRoom, Message, MessageReply 

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope['user']
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = self.room_name
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()
        
    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
    
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_content = text_data_json['message']
        attachment = text_data_json.get('attachment')

        room, created = ChatRoom.objects.get_or_create(name=self.room_name)
        message = Message.objects.create(
            room=room,
            author=self.user,
            content=message_content
        )
        
        if attachment:
            attachment_file = self.handle_attachment(attachment)
            message.attachment.save(attachment_file.name, attachment_file)
            
        message.save()

        # Example: Send message to the room group
        self.send_chat_message(message)

    def message_reply(self, message_id, author_id, content, attachment_data):
        parent_message = get_object_or_404(Message, id=message_id)
        author = get_object_or_404(settings.AUTH_USER_MODEL, id=author_id)
        
        reply_message = MessageReply.objects.create(
            message=parent_message,
            author=author,
            content=content
        )
        
        if attachment_data:
            attachment_file = self.handle_attachment(attachment_data)
            reply_message.attachment.save(attachment_file.name, attachment_file)
            
        reply_message.save()

        # Example: Send reply message to the room group
        self.send_chat_message(reply_message)

    def send_chat_message(self, message):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message.content,
                'author': message.author.username,
                'attachment': message.attachment.url if message.attachment else None,
                'timestamp': message.timestamp.strftime('%H:%M')
            }
        )
    
    def chat_message(self, event):
        self.send(text_data=json.dumps(event))
        
    def handle_attachment(self, attachment):
        format, imgstr = attachment.split(';base64,') 
        ext = format.split('/')[-1] 
        data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return data
