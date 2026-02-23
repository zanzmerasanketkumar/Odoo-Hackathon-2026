from django.contrib import admin
from .models import Student, Attendance, Performance


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'full_name', 'program', 'semester', 'email_id', 'phone_number', 'admission_year']
    list_filter = ['program', 'semester', 'admission_year', 'gender', 'blood_group']
    search_fields = ['first_name', 'last_name', 'student_id', 'email_id', 'personal_email']
    readonly_fields = ['student_id', 'email_id', 'admission_year']
    ordering = ['-student_id']
    fieldsets = (
        ('Basic Information', {
            'fields': ('first_name', 'last_name', 'date_of_birth', 'gender')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'personal_email', 'address', 'city', 'state', 'postal_code', 'country')
        }),
        ('Academic Information', {
            'fields': ('program', 'semester', 'blood_group')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_relation', 'emergency_contact_phone')
        }),
        ('System Information', {
            'fields': ('student_id', 'email_id', 'admission_year'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'date', 'is_present']
    list_filter = ['date', 'is_present']
    search_fields = ['student__name', 'student__student_id']
    date_hierarchy = 'date'


@admin.register(Performance)
class PerformanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'marks_obtained', 'total_marks', 'percentage', 'remark', 'exam_date']
    list_filter = ['subject', 'exam_date']
    search_fields = ['student__name', 'student__student_id', 'subject']
    readonly_fields = ['percentage', 'remark']
    date_hierarchy = 'exam_date'
