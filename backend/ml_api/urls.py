from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health_check, name='health'),
    path('predict/', views.predict_all, name='predict_all'),
    path('predict/stress/', views.predict_stress_level, name='predict_stress'),
    path('predict/health/', views.predict_health_score, name='predict_health'),
    path('predict/activity/', views.predict_activity_level, name='predict_activity'),
    path('predict/stress-management/', views.predict_stress_management, name='predict_stress_management'),
    path('predict/sleep/', views.predict_sleep_quality, name='predict_sleep'),
]
