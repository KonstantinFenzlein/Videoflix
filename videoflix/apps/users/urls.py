from django.urls import path
from .views import RegisterView, LoginView, LogoutView, ActivateUserView, RefreshTokenView, PasswordResetRequestView, PasswordResetConfirmView

app_name = 'users'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('activate/<str:uidb64>/<str:token>/', ActivateUserView.as_view(), name='activate'),
    path('login/', LoginView.as_view(), name='login'),
    path('refresh/', RefreshTokenView.as_view(), name='refresh'),
    path('password-reset-request/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('reset-password/<str:uidb64>/<str:token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
