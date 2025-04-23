from django.urls import path
from . import views

urlpatterns = [
    path('', views.nutrition_view, name='nutrition'),
    path('api/save-meal/', views.api_save_meal, name='api_save_meal'),
    path('api/delete-meal/<int:meal_id>/', views.api_delete_meal, name='api_delete_meal'),
    path('api/get-daily-nutrition/', views.api_get_daily_nutrition, name='api_get_daily_nutrition'),
    path('api/update-water-intake/', views.api_update_water_intake, name='api_update_water_intake'),
    path('api/search-food/', views.api_search_food, name='api_search_food'),
    path('api/save-food/', views.api_save_food, name='api_save_food'),
]