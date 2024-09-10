from django.db import models

# Create your models here.
class Cache(models.Model):
    anime_id = models.IntegerField()
    title = models.CharField(max_length=255)
    