from django.urls import path
from .views import workouts_view, workouts_api

urlpatterns = [
    path('', workouts_view, name='workouts'),
    path('api/', workouts_api, name='workouts_api'),
]