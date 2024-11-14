from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import (
    UserRegistrationViews, VerifyOTPView, LoginView,
    RegisteredUserListView, UserProfileView, CreateProfileView,
    UserDashboard, CreateRazorpayOrderView,UpdatePaymentStatusView,
    OrderCreateView, 
)

urlpatterns = [
    path('register/', UserRegistrationViews.as_view(), name='register'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('login/', LoginView.as_view(), name='login'),
    path('user-list/', RegisteredUserListView.as_view(), name="user-list"),
    path('user-profile/',UserProfileView.as_view(), name='user-profile'),
    path('create-profile/',CreateProfileView.as_view(), name='create-profile'),
    path('user-dashboard/', UserDashboard.as_view(), name='user-dashboard'),
    path('orders/create/', OrderCreateView.as_view(), name='order-create'),
    path('payment/razorpay/create/', CreateRazorpayOrderView.as_view(), name='razorpay-order-create'),
    path('payment/status/update/', UpdatePaymentStatusView.as_view(), name='payment-status-update'),
    
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
