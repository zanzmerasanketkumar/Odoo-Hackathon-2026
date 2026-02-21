from django.urls import path
from . import views

app_name = 'maintenance'

urlpatterns = [
    path('', views.MaintenanceListView.as_view(), name='maintenance_list'),
    path('create/', views.MaintenanceCreateView.as_view(), name='maintenance_create'),
    path('<int:pk>/edit/', views.MaintenanceUpdateView.as_view(), name='maintenance_edit'),
    path('<int:pk>/', views.maintenance_detail_view, name='maintenance_detail'),
    path('<int:pk>/complete/', views.maintenance_complete_view, name='maintenance_complete'),
    path('<int:pk>/parts/', views.maintenance_parts_view, name='maintenance_parts'),
    path('<int:pk>/documents/', views.maintenance_documents_view, name='maintenance_documents'),
    path('dashboard/', views.maintenance_dashboard, name='dashboard'),
]
