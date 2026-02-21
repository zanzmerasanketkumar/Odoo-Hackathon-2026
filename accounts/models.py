from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class Role(models.Model):
    ROLE_CHOICES = [
        ('fleet_manager', 'Fleet Manager'),
        ('dispatcher', 'Dispatcher'),
        ('safety_officer', 'Safety Officer'),
        ('financial_analyst', 'Financial Analyst'),
        ('admin', 'Administrator'),
    ]
    
    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Role"
        verbose_name_plural = "Roles"
    
    def __str__(self):
        return self.get_name_display()


class User(AbstractUser):
    ROLE_CHOICES = [
        ('fleet_manager', 'Fleet Manager'),
        ('dispatcher', 'Dispatcher'),
        ('safety_officer', 'Safety Officer'),
        ('financial_analyst', 'Financial Analyst'),
        ('admin', 'Administrator'),
    ]
    
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='dispatcher')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    emergency_contact = models.CharField(max_length=100, blank=True)
    emergency_phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
    
    def __str__(self):
        return f"{self.user.username}'s Profile"


class UserSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User Session"
        verbose_name_plural = "User Sessions"
        unique_together = ['user', 'session_key']
    
    def __str__(self):
        return f"{self.user.username} - {self.session_key[:8]}..."
