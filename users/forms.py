from django import forms
from django.contrib.auth.models import User
from .models import UserDetails
from django.contrib.auth import authenticate, login
from django.core.exceptions import ValidationError
from datetime import datetime
from decimal import Decimal
import re

class CustomUserCreationForm(forms.ModelForm):
    email = forms.EmailField(
        label="",
        widget=forms.EmailInput(attrs={"placeholder": "Email"})
    )
    username = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={"placeholder": "Username"})
    )
    password = forms.CharField(
        label="",
        widget=forms.PasswordInput(attrs={"placeholder": "Password"})
    )
    password2 = forms.CharField(
        label="",
        widget=forms.PasswordInput(attrs={"placeholder": "Confirm Password"})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        if not re.search(r'\d', password):
            raise forms.ValidationError("Password must contain at least one number.")
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        if password != password2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            UserDetails.objects.create(
                user=user,
                height=170,
                weight=70,
                goal='maintain',
                training_level='beginner'
            )
        return user
    
def validate_decimal(value):
    try:
        Decimal(value)
    except:
        raise ValidationError("Invalid decimal value")

class UserDetailsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Если пол уже установлен, делаем поле readonly
        if self.instance and self.instance.gender:
            self.fields['gender'].widget.attrs['readonly'] = True
            self.fields['gender'].widget.attrs['disabled'] = True
    
    class Meta:
        model = UserDetails
        fields = ['gender', 'height', 'weight', 'goal', 'training_level', 'birth_date']
        widgets = {
            'gender': forms.Select(choices=UserDetails.GENDER_CHOICES),
            'height': forms.NumberInput(attrs={'placeholder': 'Height (cm)'}),
            'goal': forms.Select(attrs={'placeholder': 'Goal'}),
            'training_level': forms.Select(attrs={'placeholder': 'Training level'}),
            'birth_date': forms.DateInput(attrs={'type': 'date', 'placeholder': 'Birth date'}),
        }

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        today = datetime.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        
        if age < 18:
            raise ValidationError("You must be at least 18 years old.")
        return birth_date

class LoginForm(forms.Form):
    email = forms.EmailField(
        label='',
        max_length=254,
        widget=forms.EmailInput(attrs={'placeholder': 'Email'})
    )
    password = forms.CharField(
        label='',
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'})
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise forms.ValidationError("No user with this email was found.")
            
            user = authenticate(username=user.username, password=password)
            if user is None:
                raise forms.ValidationError("Invalid email or password.")

        return cleaned_data