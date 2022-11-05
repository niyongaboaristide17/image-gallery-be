from django.db import models
from django.contrib.auth.models import User

import uuid

class Gallery(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
	title = models.CharField(max_length = 150)
	created_at = models.DateTimeField(auto_now_add=True)
	created_by = models.ForeignKey(User, on_delete=models.CASCADE)

class Post(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
	title = models.CharField(max_length = 150)
	image = models.ImageField(upload_to='image-upload')
	description = models.CharField(max_length = 150)
	created_at = models.DateTimeField(auto_now_add=True)
	gallery = models.ForeignKey(Gallery, on_delete=models.PROTECT)
	created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
