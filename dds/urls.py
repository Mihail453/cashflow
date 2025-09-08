from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add/', views.add_cashflow, name='add_cashflow'),
    path('edit/<int:pk>/', views.edit_cashflow, name='edit_cashflow'),
    path('delete/<int:pk>/', views.delete_cashflow, name='delete_cashflow'),
    path('statuses/', views.status_management, name='status_management'),
    path('types/', views.type_management, name='type_management'),
    path('categories/', views.category_management, name='category_management'),
    path('api/categories/', views.api_categories, name='api_categories'),
    path('api/subcategories/', views.api_subcategories, name='api_subcategories'),
    path("register/", views.register, name="register"),
]