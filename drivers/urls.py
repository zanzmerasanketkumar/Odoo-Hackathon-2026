from django.urls import path
from . import views

app_name = 'drivers'

urlpatterns = [
    path('', views.DriverListView.as_view(), name='driver_list'),
    path('create/', views.DriverCreateView.as_view(), name='driver_create'),
    path('<int:pk>/edit/', views.DriverUpdateView.as_view(), name='driver_edit'),
    path('<int:pk>/delete/', views.DriverDeleteView.as_view(), name='driver_delete'),
    path('<int:pk>/', views.driver_detail_view, name='driver_detail'),
    path('<int:pk>/performance/', views.driver_performance_view, name='driver_performance'),
    path('<int:pk>/documents/', views.driver_documents_view, name='driver_documents'),
    path('<int:pk>/documents/upload/', views.driver_document_upload, name='driver_document_upload'),
    path('<int:pk>/attendance/', views.driver_attendance_view, name='driver_attendance'),
    path('api/available/', views.get_available_drivers, name='api_available_drivers'),
    path('dashboard/', views.driver_dashboard, name='dashboard'),
]
