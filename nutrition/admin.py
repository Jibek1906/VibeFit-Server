from django.contrib import admin
from .models import DailyNutrition, Meal, FoodItem

@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'calories', 'proteins', 'fats', 'carbs', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name',)
    ordering = ('name',)
    fieldsets = (
        (None, {
            'fields': ('name',)
        }),
        ('Nutrition per 100g', {
            'fields': ('calories', 'proteins', 'fats', 'carbs'),
            'classes': ('collapse', 'wide'),
        }),
    )

@admin.register(DailyNutrition)
class DailyNutritionAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'calories', 'goal_calories', 'progress_percentage')
    list_filter = ('date', 'user')
    search_fields = ('user__username',)

@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ('nutrition', 'meal_type', 'name', 'calories', 'created_at')
    list_filter = ('meal_type', 'created_at')
    search_fields = ('name', 'nutrition__user__username')