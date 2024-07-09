from django.shortcuts import render
from rest_framework import generics
from .models import Board
from .serializers import BoardSerializer
from .filters import BoardFilter
from accounts.models import Follow
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

# Create your views here.

class BoardListCreate(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    filterset_class = BoardFilter

    def add_pin(self, request, pk=None):
        board = self.get_object()
        board.pins.add(request.data["id"])
        serializer = self.get_serializer(board)
        return Response(serializer.data)

    def followed_boards(request):
        current_user = request.user
        followed_user_ids = Follow.objects.filter(follower=current_user).values_list('followed_user_id', flat=True)
        boards = Board.objects.filter(author_id__in=followed_user_ids)
        return JsonResponse({'boards': list(boards.values())})

class BoardDetails(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Board.objects.all()
    serializer_class = BoardSerializer

