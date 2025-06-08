from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .forms import UserDetailsForm
from django.contrib.auth.models import User
from datetime import datetime
from .forms import LoginForm
from .models import UserDetails, WeightRecord
from .forms import CustomUserCreationForm
from django.http import JsonResponse
from decimal import Decimal
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

def main(request):
    return render(request, 'main.html')

def about(request):
    return render(request, 'about.html')

def analytics(request):
    total_users = User.objects.count()

    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    new_users_last_week = User.objects.filter(date_joined__gte=week_ago).count()

    recent_users = (
        User.objects.filter(date_joined__gte=today - timedelta(days=14))
        .extra({'day': "date(date_joined)"})
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )
    days = [entry['day'].strftime('%Y-%m-%d') for entry in recent_users]
    counts = [entry['count'] for entry in recent_users]

    latest_users = User.objects.order_by('-date_joined')[:5]

    return render(request, 'analytics.html', {
        'total_users': total_users,
        'new_users_last_week': new_users_last_week,
        'days': days,
        'counts': counts,
        'latest_users': latest_users,
    })

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            user_details, created = UserDetails.objects.get_or_create(
                user=user,
                defaults={
                    'height': 170,
                    'weight': 70,
                    'goal': 'maintain',
                    'training_level': 'beginner',
                    'birth_date': '2000-01-01'
                }
            )

            return redirect('user_details', user_id=user.id)
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration.html', {'form': form})

def check_email(request):
    email = request.GET.get('email', None)
    print(f"Checking email: {email}")
    if email and User.objects.filter(email=email).exists():
        return JsonResponse({'error': 'This email already in use.'})
    return JsonResponse({'success': True})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            try:
                user = User.objects.get(email=email)
                user = authenticate(request, username=user.username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('personal_office')
                else:
                    form.add_error(None, "Invalid email or password.")
            except User.DoesNotExist:
                form.add_error('email', "No user found with this email.")
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

def user_details(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    try:
        user_details = UserDetails.objects.get(user=user)
    except UserDetails.DoesNotExist:
        user_details = UserDetails.objects.create(
            user=user,
            height=170,
            weight=70,
            goal='maintain',
            training_level='beginner'
        )

    if request.method == 'POST':
        form = UserDetailsForm(request.POST, request.FILES, instance=user_details)
        if form.is_valid():
            if user_details.gender:
                details = form.save(commit=False)
                details.gender = user_details.gender
                details.save()
            else:
                form.save()
            
            user.backend = 'users.backend.EmailAuthBackend'
            login(request, user)
            return redirect('login')
    else:
        form = UserDetailsForm(instance=user_details)

    return render(request, 'user_details.html', {'form': form, 'user_details': user_details})


def calculate_age(birth_date):
    today = datetime.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

@login_required
def personal_office(request):
    user_details = get_object_or_404(UserDetails, user=request.user)
    weight_records = WeightRecord.objects.filter(user=user_details).order_by('date')
    birth_date = user_details.birth_date
    age = calculate_age(birth_date)
    labels = [record.date.strftime('%Y-%m-%d') for record in weight_records]
    weights = [float(record.weight) for record in weight_records]
    context = {
        'user_details': user_details,
        'labels': labels,
        'weights': weights,
        'age': age,
    }
    return render(request, 'personal_office.html', context)

@login_required
def update_user_details(request, user_id):
    user_details = get_object_or_404(UserDetails, user__id=user_id)
    if request.method == 'POST':
        new_weight = request.POST.get('weight')
        if new_weight:
            new_weight = Decimal(new_weight)

        new_height = request.POST.get('height')
        new_goal = request.POST.get('goal')
        new_training_level = request.POST.get('training_level')
        new_avatar = request.FILES.get('avatar')

        user_details.height = new_height
        user_details.weight = new_weight
        user_details.goal = new_goal
        user_details.training_level = new_training_level

        if new_avatar:
            user_details.avatar = new_avatar

        user_details.save()

        WeightRecord.objects.create(
            user=user_details,
            weight=new_weight,
            date=timezone.now().date()
        )

        return redirect('personal_office')
    
    weight_records = WeightRecord.objects.filter(user=user_details).order_by('date')
    labels = [record.date.strftime('%Y-%m-%d') for record in weight_records]
    weights = [record.weight for record in weight_records]

    return render(request, 'users/personal_office.html', {
        'user_details': user_details,
        'labels': labels,
        'weights': weights
    })