from django.db import models
from users.models import UserDetails
from django.db import models
from django.contrib.auth.models import User
from django.core.serializers.json import DjangoJSONEncoder

class Workout(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    video_url = models.URLField(null=True, blank=True)
    video_file = models.FileField(upload_to='workouts/', null=True, blank=True)
    goal = models.CharField(max_length=50)
    training_level = models.CharField(max_length=50)
    min_weight = models.DecimalField(max_digits=5, decimal_places=2)
    max_weight = models.DecimalField(max_digits=5, decimal_places=2)
    date = models.DateField()
    is_ai_generated = models.BooleanField(default=True)
    is_rest_day = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['date']

class GeneratedWorkoutPlan(models.Model):
   user = models.ForeignKey(User, on_delete=models.CASCADE)
   date = models.DateField()
   workouts = models.JSONField(encoder=DjangoJSONEncoder)
   created_at = models.DateTimeField(auto_now_add=True)


   class Meta:
       unique_together = ('user', 'date')