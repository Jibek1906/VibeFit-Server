from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user_details/<int:user_id>/', views.user_details, name='user_details'),
    path('personal_office/', views.personal_office, name='personal_office'),
    path('update_user_info/<int:user_id>/', views.update_user_details, name='update_user_info'),
    path('check-email/', views.check_email, name='check_email'),
]
