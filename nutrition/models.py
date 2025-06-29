from django.db import models
from users.models import UserDetails, User
from django.core.validators import MinValueValidator

class FoodItem(models.Model):
    name = models.CharField(max_length=100, unique=True)
    calories = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    proteins = models.DecimalField(max_digits=5, decimal_places=1, validators=[MinValueValidator(0)])
    fats = models.DecimalField(max_digits=5, decimal_places=1, validators=[MinValueValidator(0)])
    carbs = models.DecimalField(max_digits=5, decimal_places=1, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.calories} kcal)"

class DailyNutrition(models.Model):
    user = models.ForeignKey(UserDetails, on_delete=models.CASCADE)
    date = models.DateField()
    calories = models.PositiveIntegerField(default=0)
    proteins = models.PositiveIntegerField(default=0)
    fats = models.PositiveIntegerField(default=0)
    carbs = models.PositiveIntegerField(default=0)
    goal_calories = models.PositiveIntegerField(default=0)
    goal_proteins = models.PositiveIntegerField(default=0)
    goal_fats = models.PositiveIntegerField(default=0)
    goal_carbs = models.PositiveIntegerField(default=0)
    burned_extra_calories = models.PositiveIntegerField(default=0)
    water_intake = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="In milliliters"
    )
    
    class Meta:
        unique_together = ('user', 'date')
        verbose_name = 'Daily Nutrition'
        verbose_name_plural = 'Daily Nutrition'
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.user.username} - {self.date} - {self.calories}/{self.goal_calories}"
    
    @property
    def net_calories(self):
        return self.calories - self.burned_extra_calories


    @property
    def remaining_calories(self):
        return self.goal_calories - self.calories

    @property
    def is_calorie_deficit(self):
        return self.remaining_calories >= 0

    @property
    def progress_percentage(self):
        if self.goal_calories == 0:
            return 0
        return min(100, round((self.calories / self.goal_calories) * 100, 1))

    @property
    def protein_percentage(self):
        if self.goal_proteins == 0:
            return 0
        return min(100, round((self.proteins / self.goal_proteins) * 100, 1))

    @property
    def fat_percentage(self):
        if self.goal_fats == 0:
            return 0
        return min(100, round((self.fats / self.goal_fats) * 100, 1))

    @property
    def carb_percentage(self):
        if self.goal_carbs == 0:
            return 0
        return min(100, round((self.carbs / self.goal_carbs) * 100, 1))

class Meal(models.Model):
    MEAL_TYPES = (
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snacks', 'Snacks'),
    )

    nutrition = models.ForeignKey(DailyNutrition, on_delete=models.CASCADE, related_name='meals')
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPES)
    name = models.CharField(max_length=100)
    calories = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    proteins = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    fats = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    carbs = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    grams = models.PositiveIntegerField(default=100, validators=[MinValueValidator(1)])
    food_item = models.ForeignKey('FoodItem', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.calories} kcal)"

    class Meta:
        ordering = ['created_at']
        
class BurnedCaloriesVideo(models.Model):
    user = models.ForeignKey(UserDetails, on_delete=models.CASCADE)
    date = models.DateField()
    video_id = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    calories_burned = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=[('done', 'Done'), ('skip', 'Skip')], default='skip')

    class Meta:
        unique_together = ('user', 'date', 'video_id')