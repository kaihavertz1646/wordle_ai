from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('play/', views.play, name='play'),
    path('reset/', views.reset, name='reset'),
    path('get_user_stats/', views.get_user_stats, name='get_user_stats'),

    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]