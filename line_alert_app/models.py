from django.db import models

class LineToken(models.Model):
    access_token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    text = models.TextField()
    