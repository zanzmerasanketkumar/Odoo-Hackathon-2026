from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('reports/', views.ReportListView.as_view(), name='reports'),
    path('reports/create/', views.ReportCreateView.as_view(), name='report_create'),
    path('reports/<int:pk>/edit/', views.ReportUpdateView.as_view(), name='report_edit'),
    path('reports/<int:pk>/delete/', views.ReportDeleteView.as_view(), name='report_delete'),
    path('reports/<int:pk>/generate/', views.generate_report, name='report_generate'),
    path('alerts/', views.alerts_view, name='alerts'),
    path('alerts/<int:pk>/acknowledge/', views.acknowledge_alert, name='alert_acknowledge'),
    path('alerts/<int:pk>/resolve/', views.resolve_alert, name='alert_resolve'),
]
