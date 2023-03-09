from django.views.decorators.csrf import csrf_exempt
# csrf_exempt для отключения проверки токена через POSTMAN
from .views import (
    RegistrationView,
    UsernameValidationView,
    EmailValidationView,
    VerificationView,
    LoginView,
    LogoutView,
    ResetEmailValidationView,
    ResetPasswordView,
    CompletePasswordResetView,
    # NewPasswordValidateView
)
from django.urls import path

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('validate-username/', csrf_exempt(UsernameValidationView.as_view()), name='validate-username'),
    path('validate-email/', csrf_exempt(EmailValidationView.as_view()), name='validate-email'),
    path('activate/<uidb64>/<token>/', VerificationView.as_view(), name='activate'),
    path('validate-reset-email/', csrf_exempt(ResetEmailValidationView.as_view()), name='validate-reset-email'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('set-new-password/<uidb64>/<token>/', CompletePasswordResetView.as_view(), name='set-new-password'),
    # path('validate-new-password/', csrf_exempt(NewPasswordValidateView.as_view()), name='validate-new-password'),
]

