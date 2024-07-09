from django.db import models
from django.utils import timezone
from django.conf import settings
# Create your models here.


class Board(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='board_user')
    title = models.CharField(max_length=250)
    cover = models.ImageField(upload_to='boards', default='boards/default.png', null=True)
    is_private = models.BooleanField(default=False)
    description = models.CharField(max_length=250, blank=True)
    

    def __str__(self):
        return self.title
        