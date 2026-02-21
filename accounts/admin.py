from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, UserSession


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser', 'created_at')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'phone', 'role', 'password1', 'password2'),
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'emergency_contact', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__email', 'emergency_contact')
    readonly_fields = ('created_at', 'updated_at')
    
    def phone(self, obj):
        return obj.user.phone
    phone.short_description = 'Phone'


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip_address', 'is_active', 'created_at', 'last_activity')
    list_filter = ('is_active', 'created_at', 'last_activity')
    search_fields = ('user__username', 'ip_address', 'session_key')
    readonly_fields = ('created_at', 'last_activity')
    
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('user', 'session_key', 'ip_address', 'user_agent')
        return self.readonly_fields
