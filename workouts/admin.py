from django.contrib import admin
from .models import Workout, GeneratedWorkoutPlan

@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ('title', 'goal', 'training_level', 'is_ai_generated')
    list_filter = ('goal', 'training_level', 'is_ai_generated')
    search_fields = ('title', 'description')
    readonly_fields = ('is_ai_generated',)

@admin.register(GeneratedWorkoutPlan)
class GeneratedWorkoutPlanAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'created_at')
    list_filter = ('date', 'created_at')
    search_fields = ('user__username',)
    