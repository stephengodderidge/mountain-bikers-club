from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('member/register/', views.register, name='register'),
    path('member/login/', auth_views.LoginView.as_view(template_name='home/login.html'), name='login'),
    path('member/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('member/edit/', views.edit, name='member__edit'),
    path('member/delete/', views.delete, name='member__delete'),
    path('discover/', views.discover, name='discover')
]
