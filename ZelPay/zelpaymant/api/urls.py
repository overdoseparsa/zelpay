from django.urls import path, include
urlpatterns = [
    path('user/', include(('zelpaymant.users.urls', 'user')))

]
