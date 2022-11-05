from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Gallery, Post
from .serializers import PostSerializer, GallerySerializer

class GalleryViewSet(viewsets.ModelViewSet):

	queryset = Gallery.objects.none()
	serializer_class = GallerySerializer
	permission_classes = [IsAuthenticated,]
	filter_fields = '__all__'
	search_fields = ['title',]

	def get_queryset(self):
		return Gallery.objects.filter(created_by=self.request.user)
	

class PostViewSet(viewsets.ModelViewSet):

	queryset = Post.objects.none()
	serializer_class = PostSerializer
	permission_classes = [IsAuthenticated,]
	filter_fields = ['id', 'title', 'decription', 'created_at', 'created_by', 'gallery']
	search_fields = ['title', 'description']

	def get_queryset(self):
		return Post.objects.filter(created_by=self.request.user)