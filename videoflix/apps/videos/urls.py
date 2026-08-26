from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VideoViewSet, GenreViewSet

app_name = 'videos'

router = DefaultRouter()
router.register(r'videos', VideoViewSet, basename='video')
router.register(r'genres', GenreViewSet, basename='genre')

urlpatterns = [
    path('', include(router.urls)),
]
