from django.db import models
from django.contrib.auth.models import User

class UserDetails(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    height = models.IntegerField()
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    goal_choices = [
        ('lose-weight', 'Lose Weight'),
        ('gain-muscle', 'Gain Muscle'),
        ('maintain', 'Maintain Weight'),
    ]
    goal = models.CharField(max_length=50, choices=goal_choices)
    training_level_choices = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    training_level = models.CharField(max_length=50, choices=training_level_choices)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default_avatar.png', blank=True, null=True)
    birth_date = models.DateField(null=True)
    
    class Meta:
        verbose_name = 'user information'
        verbose_name_plural = 'user information'

    def __str__(self):
        return self.user.username


class WeightRecord(models.Model):
    user = models.ForeignKey(UserDetails, on_delete=models.CASCADE)
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    date = models.DateField()

    def __str__(self):
        return f"{self.user.user.username} - {self.date} - {self.weight} kg"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    height = models.PositiveIntegerField(default=150)
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    goal = models.CharField(max_length=50, choices=[
        ('Lose Weight', 'Lose Weight'),
        ('Gain Muscle', 'Gain Muscle'),
        ('Maintain', 'Maintain Weight')
    ], default='Maintain')
    training_level = models.CharField(max_length=50, choices=[
        ('Beginner', 'Beginner'),
        ('Int ermediate', 'Intermediate'),
        ('Advanced', 'Advanced')
    ], default='Beginner')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return self.user.username