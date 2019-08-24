from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('validate', views.ValidateView.as_view(), name='validate'),
    path('generate', views.GenerateView.as_view(), name='generate')
]
