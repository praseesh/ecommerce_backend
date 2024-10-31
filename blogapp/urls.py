from django.urls import path
from .views import UserRegistrationViews, VerifyOTPView,LoginView,RegisteredUserListView,UserDetailView

urlpatterns = [
    path('register/', UserRegistrationViews.as_view(), name='register'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('login/', LoginView.as_view(), name='login'),
    path('user-list/', RegisteredUserListView.as_view(), name="user-list"),
    path('user-profile/',UserDetailView.as_view(), name='user-profile')

]
