from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('videoflix.apps.users.urls')),
    path('api/videos/', include('videoflix.apps.videos.urls')),
]

# Medien (Videos, HLS, Thumbnails) werden nie direkt ausgeliefert, sie laufen über die API.
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
