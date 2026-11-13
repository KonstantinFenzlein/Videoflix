from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VideoViewSet, GenreViewSet

app_name = 'videos'

router = DefaultRouter()
# Der Slash am Ende ist optional, damit relative HLS-Segmentpfade ohne Redirect funktionieren.
# DRF akzeptiert im Konstruktor nur einen Bool, deshalb wird das Attribut direkt gesetzt.
router.trailing_slash = '/?'
router.register(r'videos', VideoViewSet, basename='video')
router.register(r'genres', GenreViewSet, basename='genre')

urlpatterns = [
    path('', include(router.urls)),
]
