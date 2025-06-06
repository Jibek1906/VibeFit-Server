# Generated by Django 5.1.6 on 2025-04-22 14:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nutrition', '0007_ingredient_remove_mealfooditem_food_item_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='FoodItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('calories', models.PositiveIntegerField(help_text='Calories per 100g')),
                ('proteins', models.PositiveIntegerField(help_text='Proteins per 100g (g)')),
                ('fats', models.PositiveIntegerField(help_text='Fats per 100g (g)')),
                ('carbs', models.PositiveIntegerField(help_text='Carbs per 100g (g)')),
            ],
        ),
        migrations.RemoveField(
            model_name='meal',
            name='ingredients',
        ),
        migrations.RemoveField(
            model_name='mealingredient',
            name='ingredient',
        ),
        migrations.RemoveField(
            model_name='mealingredient',
            name='meal',
        ),
        migrations.CreateModel(
            name='MealFoodItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveIntegerField(help_text='Amount in grams')),
                ('food_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nutrition.fooditem')),
                ('meal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nutrition.meal')),
            ],
        ),
        migrations.AddField(
            model_name='meal',
            name='food_items',
            field=models.ManyToManyField(through='nutrition.MealFoodItem', to='nutrition.fooditem'),
        ),
        migrations.DeleteModel(
            name='Ingredient',
        ),
        migrations.DeleteModel(
            name='MealIngredient',
        ),
    ]
