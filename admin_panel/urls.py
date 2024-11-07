from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import (
    AdminLoginView,AdminDashboardView,AdminUserView
)

urlpatterns = [
    path('login/', AdminLoginView.as_view(), name='login'),
    path('dashboard/', AdminDashboardView.as_view(), name='dashboard'),
    path('users/', AdminUserView.as_view(), name='admin-user-list'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
