from django.urls import path
from accounts.views import *

urlpatterns = [
    path('register', Register.as_view(),name='register'),
    path('login', LogIn.as_view(),name='login'),
    path('logout', LogOut.as_view(),name='logout'),
    path('token/refresh', RefreshTokenView.as_view(),name='refresh_token'),
]