from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('download_pdf/', views.download_pdf, name='download_pdf'),
    path('ocr-upload/', views.ocr_upload, name='ocr_upload'),
]
