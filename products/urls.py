from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    CartView, # ProductListAndFilterAPIView,CheckoutAPIView
)
urlpatterns = [
    path('cart/', CartView.as_view(), name='cart'),
    # path('products-list-filter/', ProductListAndFilterAPIView.as_view(), name='product-list'),
    # path('checkout/', CheckoutAPIView.as_view(), name='checkout'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
