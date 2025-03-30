from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from datetime import datetime, timedelta
from .models import DailyNutrition, Meal
from users.models import UserDetails
import json
from django.views.decorators.csrf import csrf_exempt

@login_required
def calculate_daily_calories(user_details):
    age = (datetime.now().date() - user_details.birth_date).days // 365 if user_details.birth_date else 30
    weight = float(user_details.weight)
    height = user_details.height
    gender = user_details.gender
    goal = user_details.goal
    training_level = user_details.training_level

    if gender == 'male':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    activity_multipliers = {
        'beginner': 1.2,
        'intermediate': 1.375,
        'advanced': 1.55
    }
    activity_multiplier = activity_multipliers.get(training_level, 1.2)
    tdee = bmr * activity_multiplier

    if goal == 'lose-weight':
        calories = tdee * 0.85
    elif goal == 'gain-muscle':
        calories = tdee * 1.15
    else:
        calories = tdee

    if goal == 'gain-muscle':
        proteins = weight * (2.2 if gender == 'male' else 1.8)
        fats = weight * (1 if gender == 'male' else 0.8)
    elif goal == 'lose-weight':
        proteins = weight * (2.0 if gender == 'male' else 1.6)
        fats = weight * (0.8 if gender == 'male' else 0.7)
    else:
        proteins = weight * (1.6 if gender == 'male' else 1.4)
        fats = weight * (0.8 if gender == 'male' else 0.7)

    carbs = (calories - (proteins * 4 + fats * 9)) / 4

    return {
        'calories': round(calories),
        'proteins': round(proteins),
        'fats': round(fats),
        'carbs': round(carbs),
        'water_intake': round(weight * 35)
    }

@login_required
def nutrition_view(request):
    user_details = UserDetails.objects.get(user=request.user)
    today = datetime.now().date()

    try:
        daily_nutrition = DailyNutrition.objects.get(user=user_details, date=today)
    except DailyNutrition.DoesNotExist:
        calculated = calculate_daily_calories(user_details)
        daily_nutrition = DailyNutrition.objects.create(
            user=user_details,
            date=today,
            goal_calories=calculated['calories'],
            goal_proteins=calculated['proteins'],
            goal_fats=calculated['fats'],
            goal_carbs=calculated['carbs'],
            calories=0,
            proteins=0,
            fats=0,
            carbs=0,
            water_intake=0
        )
    else:
        calculated = calculate_daily_calories(user_details)
        needs_update = (
            daily_nutrition.goal_calories != calculated['calories'] or
            daily_nutrition.goal_proteins != calculated['proteins'] or
            daily_nutrition.goal_fats != calculated['fats'] or
            daily_nutrition.goal_carbs != calculated['carbs']
        )
        
        if needs_update:
            daily_nutrition.goal_calories = calculated['calories']
            daily_nutrition.goal_proteins = calculated['proteins']
            daily_nutrition.goal_fats = calculated['fats']
            daily_nutrition.goal_carbs = calculated['carbs']
            daily_nutrition.save()

    meals = Meal.objects.filter(nutrition=daily_nutrition).order_by('meal_type')
    
    context = {
        'daily_nutrition': daily_nutrition,
        'meals': meals,
        'water_goal': round(float(user_details.weight) * 35)
    }
    return render(request, 'nutrition.html', context)

@login_required
@csrf_exempt
def api_save_meal(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_details = UserDetails.objects.get(user=request.user)
            date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            
            daily_nutrition, created = DailyNutrition.objects.get_or_create(
                user=user_details,
                date=date,
                defaults={
                    'calories': 0,
                    'proteins': 0,
                    'fats': 0,
                    'carbs': 0,
                    **calculate_daily_calories(user_details)
                }
            )

            meal = Meal.objects.create(
                nutrition=daily_nutrition,
                meal_type=data['meal_type'],
                name=data['name'],
                calories=data['calories'],
                proteins=data['proteins'],
                fats=data['fats'],
                carbs=data['carbs']
            )

            daily_nutrition.calories += data['calories']
            daily_nutrition.proteins += data['proteins']
            daily_nutrition.fats += data['fats']
            daily_nutrition.carbs += data['carbs']
            daily_nutrition.save()

            return JsonResponse({
                'status': 'success',
                'message': 'Meal saved successfully',
                'meal_id': meal.id
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'error': str(e)
            }, status=400)
    return JsonResponse({
        'status': 'error',
        'error': 'Invalid request method'
    }, status=405)

@login_required
@csrf_exempt
def api_update_goals(request):
    if request.method == 'POST':
        try:
            user_details = UserDetails.objects.get(user=request.user)
            today = datetime.now().date()
            
            daily_nutrition, created = DailyNutrition.objects.get_or_create(
                user=user_details,
                date=today,
                defaults={
                    'calories': 0,
                    'proteins': 0,
                    'fats': 0,
                    'carbs': 0
                }
            )
            
            calculated = calculate_daily_calories(user_details)
            daily_nutrition.goal_calories = calculated['calories']
            daily_nutrition.goal_proteins = calculated['proteins']
            daily_nutrition.goal_fats = calculated['fats']
            daily_nutrition.goal_carbs = calculated['carbs']
            daily_nutrition.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Goals updated successfully',
                'goals': calculated
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'error': str(e)
            }, status=400)
    return JsonResponse({
        'status': 'error',
        'error': 'Invalid request method'
    }, status=405)

@login_required
@csrf_exempt
def api_update_water_intake(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_details = UserDetails.objects.get(user=request.user)
            date = datetime.strptime(data['date'], '%Y-%m-%d').date()

            daily_nutrition, created = DailyNutrition.objects.get_or_create(
                user=user_details,
                date=date,
                defaults={
                    'water_intake': data['amount'],
                    **calculate_daily_calories(user_details)
                }
            )

            if not created:
                daily_nutrition.water_intake = data['amount']
                daily_nutrition.save()

            return JsonResponse({
                'status': 'success',
                'water_intake': daily_nutrition.water_intake
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'error': str(e)
            }, status=400)
    return JsonResponse({
        'status': 'error',
        'error': 'Invalid request method'
    }, status=405)

@login_required
@csrf_exempt
def api_get_daily_nutrition(request):
    if request.method == 'GET':
        try:
            user_details = UserDetails.objects.get(user=request.user)
            date_str = request.GET.get('date', datetime.now().date().strftime('%Y-%m-%d'))
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            daily_nutrition, created = DailyNutrition.objects.get_or_create(
                user=user_details,
                date=date,
                defaults={
                    **calculate_daily_calories(user_details),
                    'calories': 0,
                    'proteins': 0,
                    'fats': 0,
                    'carbs': 0
                }
            )
            
            meals = Meal.objects.filter(nutrition=daily_nutrition).order_by('meal_type')
            
            return JsonResponse({
                'status': 'success',
                'date': date_str,
                'calories': daily_nutrition.calories,
                'proteins': daily_nutrition.proteins,
                'fats': daily_nutrition.fats,
                'carbs': daily_nutrition.carbs,
                'goal_calories': daily_nutrition.goal_calories,
                'goal_proteins': daily_nutrition.goal_proteins,
                'goal_fats': daily_nutrition.goal_fats,
                'goal_carbs': daily_nutrition.goal_carbs,
                'water_intake': daily_nutrition.water_intake,
                'meals': [{
                    'id': meal.id,
                    'meal_type': meal.meal_type,
                    'name': meal.name,
                    'calories': meal.calories,
                    'proteins': meal.proteins,
                    'fats': meal.fats,
                    'carbs': meal.carbs,
                    'created_at': meal.created_at.strftime('%H:%M')
                } for meal in meals]
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'error': str(e)
            }, status=400)
    return JsonResponse({
        'status': 'error',
        'error': 'Invalid request method'
    }, status=405)

@login_required
@csrf_exempt
def api_delete_meal(request, meal_id):
    if request.method == 'DELETE':
        try:
            meal = Meal.objects.get(id=meal_id, nutrition__user__user=request.user)
            daily_nutrition = meal.nutrition
            
            daily_nutrition.calories -= meal.calories
            daily_nutrition.proteins -= meal.proteins
            daily_nutrition.fats -= meal.fats
            daily_nutrition.carbs -= meal.carbs
            daily_nutrition.save()
            
            meal.delete()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Meal deleted successfully'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'error': str(e)
            }, status=400)
    return JsonResponse({
        'status': 'error',
        'error': 'Invalid request method'
    }, status=405)