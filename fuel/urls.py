from django.urls import path
from . import views

app_name = 'fuel'

urlpatterns = [
    path('logs/', views.FuelLogListView.as_view(), name='fuel_log_list'),
    path('logs/create/', views.FuelLogCreateView.as_view(), name='fuel_log_create'),
    path('expenses/', views.ExpenseListView.as_view(), name='expense_list'),
    path('expenses/create/', views.ExpenseCreateView.as_view(), name='expense_create'),
    path('budgets/', views.FuelBudgetListView.as_view(), name='fuel_budget_list'),
    path('budgets/create/', views.FuelBudgetCreateView.as_view(), name='fuel_budget_create'),
    path('dashboard/', views.fuel_dashboard, name='dashboard'),
    path('reports/efficiency/', views.fuel_efficiency_report, name='fuel_efficiency_report'),
    path('api/stats/', views.get_fuel_stats, name='api_fuel_stats'),
]
