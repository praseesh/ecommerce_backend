from django.urls import path
from .views import UserRegistrationViews, VerifyOTPView,LoginView,PostView

urlpatterns = [
    path('register/', UserRegistrationViews.as_view(), name='register'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('login/', LoginView.as_view(), name='login'),
    path('posts/', PostView.as_view(), name="post"),
    # path('send-otp/',SendOtp.as_view(), name="send-otp" ),
    # path('send_wel/', send_wel, name="send_wel")
]
