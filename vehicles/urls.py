from django.urls import path
from . import views

app_name = 'vehicles'

urlpatterns = [
    path('', views.VehicleListView.as_view(), name='vehicle_list'),
    path('create/', views.VehicleCreateView.as_view(), name='vehicle_create'),
    path('<int:pk>/delete/', views.VehicleDeleteView.as_view(), name='vehicle_delete'),
    path('<int:pk>/', views.vehicle_detail_view, name='vehicle_detail'),
    path('<int:pk>/edit/', views.VehicleUpdateView.as_view(), name='vehicle_edit'),
    path('<int:pk>/documents/', views.vehicle_documents_view, name='vehicle_documents'),
    path('documents/<int:document_id>/delete/', views.vehicle_document_delete_view, name='vehicle_document_delete'),
    path('api/available/', views.get_available_vehicles, name='api_available_vehicles'),
    path('api/check-capacity/', views.check_vehicle_capacity, name='api_check_capacity'),
]
