from django.db import models

from src.core import settings


class Post(models.Model):
    STATUS_CHOICES = [
        ('draft', 'DRAFT'),
        ('published', 'PUBLISHED')
    ]

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    body = models.CharField(max_length = 1000)
    photo = models.ImageField(upload_to='post_photos/', blank=True, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title