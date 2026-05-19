from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from core import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/tts/', views.tts_api, name='tts_api'),
    path('api/voices/', views.voices_api, name='voices_api'),
    path('api/download/<str:filename>/', views.download_audio, name='download_audio'),
    path('blog/', views.blog, name='blog'),
    path('api-docs/', views.api_docs, name='api_docs'),
    path('privacy/', views.privacy, name='privacy'),
    path('terms/', views.terms, name='terms'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
