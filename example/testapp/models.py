from django.db import models


# Create your models here.
class Topic(models.Model):
    title = models.CharField(max_length=255)
    icon = models.FileField(upload_to="uploads")
