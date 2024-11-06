from django.urls import path
from . import views
urlpatterns = [
    path('cache_set_get_method/', views.cache_set_get_method, name='cache_example')
]
