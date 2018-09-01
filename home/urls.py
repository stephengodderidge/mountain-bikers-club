from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('member/register/', views.register, name='register'),
    path('member/login/', auth_views.LoginView.as_view(template_name='home/login.html'), name='login'),
    path('member/logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('member/password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('member/password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),

    # path('member/password_reset/', auth_views.PasswordResetView.as_view() ,name='password_reset'),
    # path('member/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    # path('member/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    # path('member/reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_complete'),

    path('member/edit/', views.edit, name='member__edit'),
    path('member/delete/', views.delete, name='member__delete'),
    path('discover/', views.discover, name='discover'),
]
