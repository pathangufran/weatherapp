from django.urls import path
from cities.views import *

urlpatterns = [
    path('add/',AddCity.as_view(),name='add'),
    path('get/',GetCity.as_view(),name='get'),
    path('delete/',DeleteCity.as_view(),name='delete')
]