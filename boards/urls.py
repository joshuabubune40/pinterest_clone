from django.urls import path
from .views import BoardListCreate, BoardDetails

urlpatterns = [
    path('boards/', BoardListCreate.as_view(), name='board-list-create'),
    path('boards/<int:pk>/', BoardDetails.as_view(), name='boards-details')
]
