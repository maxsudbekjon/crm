from django.urls import path
from .views import *
app_name = "Auth"

urlpatterns = [
    path('signup/', SignupView.as_view()),
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),

    path('profile/', ProfileView.as_view()),
    path('profile/update/', ProfileUpdateView.as_view()),

    path('password/change/', PasswordChangeView.as_view()),
    path('password/forgot/', ForgotPasswordView.as_view()),
    path('password/verify/', VerifyResetCodeView.as_view()),
    path('password/reset/', ResetPasswordView.as_view()),

]