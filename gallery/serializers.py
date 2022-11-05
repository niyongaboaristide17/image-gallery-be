from rest_framework import serializers
from .models import Gallery, Post

class GallerySerializer(serializers.ModelSerializer):

	class Meta:
		model = Gallery
		fields = '__all__'


class PostSerializer(serializers.ModelSerializer):

	class Meta:
		model = Post
		fields = '__all__'
