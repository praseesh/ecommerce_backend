from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
    path('chatbot/', include('chatbot.urls')),
    path('admin_panel/', include('admin_panel.urls')),
    path('products/', include('products.urls')),
    
]
