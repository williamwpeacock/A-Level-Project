from django.urls import path, re_path
from . import views

app_name = 'login'

urlpatterns = [
    path('', views.LoginView.as_view(), name='login'),
    path('enterpin', views.EnterPINView.as_view(), name='enterpin'),
    re_path(r'^enterpin/(?P<pin>[0-9]+)$', views.RegisterView.as_view(), name='register'),
    path('success', views.SuccessView.as_view(), name='success'),
    path('logout', views.my_logout, name='logout'),
]
