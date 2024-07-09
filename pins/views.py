from rest_framework import generics, viewsets, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import redirect
from django.http import JsonResponse
from .models import Pin, Comment, CommentReplies, LikePins, SavePins
from .serializers import PinSerializer, CommentSerializer, CommentRepliesSerializer
from .filters import PinFilter
from accounts.models import Follow
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

class PinListCreate(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated] 
    queryset = Pin.objects.all()
    serializer_class = PinSerializer
    filterset_class = PinFilter

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by followed users
        if self.request.query_params.get('followed', None):
            current_user = self.request.user
            followed_user_ids = Follow.objects.filter(follower=current_user).values_list('followed_user_id', flat=True)
            queryset = queryset.filter(user_id__in=followed_user_ids)

        # Filter by tags
        tags = self.request.query_params.get('tags', None)
        if tags:
            tags_list = tags.split(',')
            for tag in tags_list:
                queryset = queryset.filter(tags__icontains=tag)
            queryset = queryset.distinct()

        return queryset



class LikePin(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated] 

    def post(self, request, pin_id):
        try:
            pin = Pin.objects.get(pk=pin_id)
        except Pin.DoesNotExist:
            return Response({'error': 'Pin not found'}, status=status.HTTP_404_NOT_FOUND)

        user = request.user

        try:
            like = LikePins.objects.get(user=user, pin=pin)
            # If the user has already liked the pin, unlike it
            like.delete()
            message = 'Pin unliked successfully'
        except LikePins.DoesNotExist:
            # Otherwise, like the pin
            LikePins.objects.create(user=user, pin=pin)
            message = 'Pin liked successfully'

        return Response({'message': message}, status=status.HTTP_200_OK)


class SavePin(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated] 

    def post(self, request, pin_id):
        try:
            pin = Pin.objects.get(pk=pin_id)
        except Pin.DoesNotExist:
            return Response({'error': 'Pin not found'}, status=status.HTTP_404_NOT_FOUND)

        user = request.user

        try:
            saved_pin = SavePins.objects.get(user=user, pin=pin)
            # If the user has already saved the pin, unsave it
            saved_pin.delete()
            message = 'Pin unsaved successfully'
        except SavePins.DoesNotExist:
            # Otherwise, save the pin
            SavePins.objects.create(user=user, pin=pin)
            message = 'Pin saved successfully'

        return Response({'message': message}, status=status.HTTP_200_OK)
class UserCreatedPins(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated] 
    serializer_class = PinSerializer

    def get_queryset(self):
        user = self.request.user
        return Pin.objects.filter(user=user)

class UserSavedPins(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated] 
    serializer_class = PinSerializer

    def get_queryset(self):
        user = self.request.user
        return Pin.objects.filter(savepins__user=user)
class PinDetails(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated] 
    queryset = Pin.objects.all()
    serializer_class = PinSerializer

class CommentListCreate(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]  
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    
class CommentRepliesCreate(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]  
    queryset = CommentReplies.objects.all()
    serializer_class = CommentRepliesSerializer
    
class CommentDetails(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]  
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    
class CommentReplyDetails(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]  
    queryset = CommentReplies.objects.all()
    serializer_class = CommentRepliesSerializer