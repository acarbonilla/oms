from django.urls import path
from .views import omsLogin, omsLogout

urlpatterns = [
    path('', omsLogin, name='omsLogin'),
    path('logout/', omsLogout, name='omsLogout'),
    ]