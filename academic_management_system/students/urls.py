from django.urls import path
from . import views

urlpatterns = [
    path('', views.student_list, name='student_list'),
    path('create/', views.student_create, name='student_create'),
    path('<int:pk>/', views.student_detail, name='student_detail'),
    path('<int:pk>/update/', views.student_update, name='student_update'),
    path('<int:pk>/delete/', views.student_delete, name='student_delete'),
    path('<int:pk>/report/', views.student_report, name='student_report'),
    path('<int:pk>/report/csv/', views.student_report_csv, name='student_report_csv'),
    path('all-students/csv/', views.all_students_csv, name='all_students_csv'),
    path('attendance/csv/', views.attendance_csv, name='attendance_csv'),
    path('attendance/', views.attendance_management, name='attendance_management'),
    path('attendance/edit/<int:student_id>/', views.attendance_edit, name='attendance_edit'),
    path('attendance/history/<int:student_id>/', views.attendance_history, name='attendance_history'),
    path('performance/', views.performance_management, name='performance_management'),
    path('fix-email-mismatches/', views.fix_email_mismatches, name='fix_email_mismatches'),
]
