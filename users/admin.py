from django.contrib import admin
from .models import UserDetails

@admin.register(UserDetails)
class UserDetailsAdmin(admin.ModelAdmin):
    list_display = ('user', 'height', 'weight', 'goal', 'training_level')