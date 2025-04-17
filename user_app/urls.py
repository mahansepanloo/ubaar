from django.urls import path
from .views import SendOTPView, VerifyOTPView, LoginView, CompleteProfileView

urlpatterns = [
    path('send-otp/', SendOTPView.as_view(), name='send_otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('login/', LoginView.as_view(), name='login'),
    path('complete-profile/', CompleteProfileView.as_view(), name='complete_profile'),
]