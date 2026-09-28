from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.get_products),
    path('products/<int:pk>/', views.get_product),
    path('categories/', views.get_categories),
    path('user_profiles/', views.get_user_profiles),
    path('profile/', views.user_profile),
    path('cart/', views.get_cart),
    path('cart/add/', views.add_to_cart),
    path('cart/remove/', views.remove_from_cart),
    path('cart/update/', views.update_cart_quantity),
    path('leaderboard/', views.leaderboard),
    path('score/', views.update_score),
    path('admin/stats/', views.admin_stats),
    path('admin/analytics/', views.admin_analytics),
    path('admin/users/', views.admin_users),
    path('admin/users/<int:pk>/', views.admin_user_detail),
]

