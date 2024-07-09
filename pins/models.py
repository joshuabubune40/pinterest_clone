from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.conf import settings
from django.utils import timezone
from boards.models import Board
from accounts.models import User
from mimetypes import guess_type
from django.core.exceptions import ValidationError



class Pin(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='pin_user'
    )
    board = models.ForeignKey(
        Board, on_delete=models.CASCADE, related_name='pins_set'
    )
    image = models.ImageField(upload_to='pins/images', null=False, blank=True)
    video = models.FileField(upload_to='pins/videos', null=False, blank=True)
    title = models.CharField(max_length=250)
    link = models.CharField(max_length=250, null=True)
    description = models.TextField()
    date_created = models.DateTimeField(default=timezone.now)
    likes = models.ManyToManyField(User, related_name='liked_pins', blank=True)

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        if self.image and self.video:
            raise ValidationError("You can upload either an image or a video, but not both.")
        if not self.image and not self.video:
            raise ValidationError("You must upload either an image or a video.")


    def get_shareable_url(self):
        return f'http://localhost:8000/pins/{self.pk}/'

class LikePins(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pin = models.ForeignKey(Pin, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'pin')

    def __str__(self):
        return f'{self.user.username} likes {self.pin.title}'

class SavePins(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pin = models.ForeignKey(Pin, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'pin')

    def __str__(self):
        return f'{self.user.username} saved {self.pin.title}'


class Comment(models.Model):
    pin = models.ForeignKey(Pin, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=255, null=False, default='comment on this')
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'Comment by {self.user.username} on {self.pin}'
    
class CommentReplies(models.Model):
    comment = models.ForeignKey(Comment, related_name='replies', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    parent_reply = models.ForeignKey('self', related_name='replies', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return f'Reply by {self.user.username} to {self.comment}'

    
