from django.urls import path
from .views import UserRegistrationViews, VerifyOTPView,LoginView,UserListView

urlpatterns = [
    path('register/', UserRegistrationViews.as_view(), name='register'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('login/', LoginView.as_view(), name='login'),
    path('user-list/', UserListView.as_view(), name="user-list"),

]
