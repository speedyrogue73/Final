from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.profile_view, name='profile'),
    path('favorites/<int:pk>/remove/', views.remove_favorite_view, name='remove_favorite'),
]
