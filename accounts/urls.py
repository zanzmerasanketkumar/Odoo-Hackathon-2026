from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.UserProfileUpdateView.as_view(), name='edit_profile'),
    path('password/change/', views.CustomPasswordChangeView.as_view(), name='password_change'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
]
