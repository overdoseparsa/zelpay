from django.urls import path
from .apis import ProfileApi, RegisterApi , LogginProfileApi
from django.http import  HttpRequest

urlpatterns = [
    path('register/', RegisterApi.as_view(),name="register"),
    path('profile/', ProfileApi.as_view(),name="profile"),
    path('loggin/',LogginProfileApi.as_view(),name='loggin')
]
