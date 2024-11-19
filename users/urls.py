from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import (
    UserRegistrationViews, VerifyOTPView, LoginView,
    RegisteredUserListView, UserProfileView, CreateProfileView,
    UserDashboard, CreateRazorPayPaymentPage,UpdatePaymentStatusView,
    OrderCreateView, CashOnDelivery,VerifyRazorPayPayment
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
    path('payment/razorpay/create/', CreateRazorPayPaymentPage.as_view(), name='razorpay-order-create'),
    path('payment/status/update/', UpdatePaymentStatusView.as_view(), name='payment-status-update'),
    path('unpaid/order/',UnpaidOrdersTotalView.as_view(), name='unpaid-order'),
    path('verify/payment/', VerifyRazorPayPayment.as_view(), name='verify-payment'),
    path('cod/order/',UnpaidOrdersTotalView.as_view(), name='unpaid-order'),
    
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
