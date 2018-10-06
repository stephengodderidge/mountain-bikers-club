from django.contrib.auth.decorators import login_required
from django.urls import path
from django.contrib.auth import views as auth_views

from .views import MemberDelete
from . import views


class AuthenticationForm(auth_views.AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['autocomplete'] = 'username'
        self.fields['password'].widget.attrs['autocomplete'] = 'current-password'


urlpatterns = [
    path('@<slug>/edit/', views.edit, name='member__edit'),
    path('@<slug>/delete/', login_required(MemberDelete.as_view()), name='member__delete'),
    path('@<slug>/', views.main, name='member__main'),

    path('member/register/', views.register, name='register'),
    path('member/login/', auth_views.LoginView.as_view(template_name='member/login.html', authentication_form=AuthenticationForm), name='login'),
    path('member/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('member/password_change/', auth_views.PasswordChangeView.as_view(template_name='member/password_change.html'), name='password_change'),
    path('member/password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='member/password_change_done.html'), name='password_change_done'),
    path('member/password_reset/', auth_views.PasswordResetView.as_view(template_name='member/password_reset.html') ,name='password_reset'),
    path('member/password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='member/password_reset_done.html'), name='password_reset_done'),
    path('member/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='member/password_reset_confirm.html'), name='password_reset_confirm'),
    path('member/reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='member/password_reset_complete.html'), name='password_reset_complete'),
]
