from django.urls import path

from .views import (
    PinListCreate,
    PinDetails,
    SavePin,
    UserCreatedPins,
    UserSavedPins,
    CommentListCreate,
    CommentDetails,
    CommentRepliesCreate,
    CommentReplyDetails,
    LikePin
)

urlpatterns = [
    path('pins/', PinListCreate.as_view(), name='pin-list-create'),
    path('pins/<int:pk>/', PinDetails.as_view(), name='pin-details'),
    path('pins/<int:pin_id>/save/', SavePin.as_view(), name='save-pin'),
    path('pins/<int:pin_id>/like/', LikePin.as_view(), name="like-pin"),
    path('pins/created/', UserCreatedPins.as_view(), name='user-created-pins'),
    path('pins/saved/', UserSavedPins.as_view(), name='user-saved-pins'),

    path('pins/<int:pin_id>/comments/', CommentListCreate.as_view(), name='comment-list-create'),
    path('pins/<int:pin_id>/comments/<int:pk>/', CommentDetails.as_view(), name='comment-detail'),
    path('pins/<int:pin_id>/comments/<int:pk>/replies/', CommentRepliesCreate.as_view(), name='comment-replies-create'),
    path('pins/<int:pin_id>/comments/<int:pk>/replies/<int:reply_pk>/', CommentReplyDetails.as_view(), name='reply-detail'),
]
