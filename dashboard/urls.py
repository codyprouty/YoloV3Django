from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('photo/<str:pk>/', views.viewPhoto, name='photo'),
    path('config/<str:pk>/', views.viewConfig, name='config'),
    path('addphoto/', views.addPhoto, name='addphoto'),
    path('addconfig/', views.addConfig, name='addconfig'),
    path('detection/', views.detection, name='detection'),
    path('selectFiles/', views.selectFiles, name='selectFiles'),
    path('deletephoto/', views.deletephoto, name='deletephoto'),
    path('deleteconfig/', views.deleteconfig, name='deleteconfig'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)