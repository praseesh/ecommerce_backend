from django.urls import path
from . import views
urlpatterns = [
    path('cache-example/', views.cache_example_view, name='cache_example'),
]
