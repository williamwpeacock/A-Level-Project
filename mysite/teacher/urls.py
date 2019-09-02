from django.urls import path, re_path
from . import views

app_name = 'teacher'

urlpatterns = [
    path('', views.WelcomeView.as_view(), name='welcome'),
    re_path(r'^(?P<pe_id>[0-9]+)/$', views.ParentsEveningView.as_view(), name='parentsevening'),
    re_path(r'^(?P<pe_id>[0-9]+)/(?P<class_id>[0-9]+)$', views.ClassView.as_view(), name='class'),
    re_path(r'^(?P<pe_id>[0-9]+)/(?P<class_id>[0-9]+)/book/(?P<timeslot>[0-9]{4})$', views.BookView.as_view(), name='book'),
    re_path(r'^(?P<pe_id>[0-9]+)/(?P<class_id>[0-9]+)/view/(?P<timeslot>[0-9]{4})$', views.ViewBookingView.as_view(), name='view'),
    re_path(r'^(?P<pe_id>[0-9]+)/(?P<class_id>[0-9]+)/remove/(?P<timeslot>[0-9]{4})$', views.RemoveBookingView.as_view(), name='remove'),
]
