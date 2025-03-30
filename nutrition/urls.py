from django.urls import path
from . import views

urlpatterns = [
    path('', views.nutrition_view, name='nutrition'),
    path('api/save-meal/', views.api_save_meal, name='api_save_meal'),
    path('api/delete-meal/<int:meal_id>/', views.api_delete_meal, name='api_delete_meal'),
    path('api/get-daily-nutrition/', views.api_get_daily_nutrition, name='api_get_daily_nutrition'),
    path('api/update-water-intake/', views.api_update_water_intake, name='api_update_water_intake'),
    path('api/update-goals/', views.api_update_goals, name='api_update_goals'),
]