from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import PostViewSet, GalleryViewSet

routes = DefaultRouter(trailing_slash=False)

routes.register('galleries', GalleryViewSet, basename='galleries')
routes.register('posts', PostViewSet, basename='posts')

urlpatterns = [
    path("", include(routes.urls)),
]