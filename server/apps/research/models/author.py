# author.py
from django.contrib.auth.models import User
from django.db import models
from apps.common.models import BaseModel

class Author(BaseModel):
    """Model for authors."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    twitter_username = models.CharField(max_length=100, blank=True, null=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Authors'
        
    def __str__(self):
        return self.user.get_full_name() or self.user.username