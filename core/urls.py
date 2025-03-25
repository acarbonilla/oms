from django.urls import path
from .views import defaultPage, group_based_redirect

urlpatterns = [
    path('', defaultPage, name='defaultPage'),
    path('group_based_redirect/', group_based_redirect, name='group_based_redirect'),

]
