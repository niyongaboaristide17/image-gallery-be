from rest_framework import serializers
from .models import Gallery, Post

class GallerySerializer(serializers.ModelSerializer):
	created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
	class Meta:
		model = Gallery
		fields = '__all__'


class PostSerializer(serializers.ModelSerializer):
	created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
	class Meta:
		model = Post
		fields = '__all__'
