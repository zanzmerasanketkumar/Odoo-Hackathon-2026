from django.urls import path
from . import views

app_name = 'trips'

urlpatterns = [
    path('', views.TripListView.as_view(), name='trip_list'),
    path('create/', views.TripCreateView.as_view(), name='trip_create'),
    path('<int:pk>/edit/', views.TripUpdateView.as_view(), name='trip_edit'),
    path('<int:pk>/delete/', views.TripDeleteView.as_view(), name='trip_delete'),
    path('<int:pk>/', views.trip_detail_view, name='trip_detail'),
    path('<int:pk>/dispatch/', views.trip_dispatch_view, name='trip_dispatch'),
    path('<int:pk>/start/', views.trip_start_view, name='trip_start'),
    path('<int:pk>/complete/', views.trip_complete_view, name='trip_complete'),
    path('<int:pk>/cancel/', views.trip_cancel_view, name='trip_cancel'),
    path('<int:pk>/expenses/', views.trip_expenses_view, name='trip_expenses'),
    path('<int:pk>/expenses/add/', views.trip_expense_create_view, name='trip_expense_create'),
    path('<int:pk>/checkpoints/', views.trip_checkpoints_view, name='trip_checkpoints'),
    path('<int:pk>/documents/', views.trip_documents_view, name='trip_documents'),
    path('dashboard/', views.trip_dashboard, name='dashboard'),
    path('api/stats/', views.get_trip_stats, name='api_stats'),
]
