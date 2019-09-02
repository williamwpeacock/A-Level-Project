from django.urls import path, re_path, include

from . import views

app_name = 'admin'

urlpatterns = [
    path('', views.WelcomeView.as_view(), name="welcome"),
    path('accounts/', views.AccountsView.as_view(), name="accounts"),
    re_path(r'^accounts/add/(?P<role>\bstudent\b|\bparent\b|\bteacher\b|\badmin\b)$', views.AddAccountView.as_view(), name="addaccount"),
    re_path(r'^accounts/edit/(?P<account_id>[0-9]+)$', views.EditAccountView.as_view(), name="editaccount"),
    re_path(r'^accounts/delete/(?P<account_id>[0-9]+)$', views.DeleteAccountView.as_view(), name="deleteaccount"),
    path('classes/', views.ClassesView.as_view(), name="classes"),
    path('classes/add', views.AddClassView.as_view(), name="addclass"),
    re_path(r'^classes/edit/(?P<class_id>[0-9]+)$', views.EditClassView.as_view(), name="editclass"),
    re_path(r'^classes/delete/(?P<class_id>[0-9]+)$', views.DeleteClassView.as_view(), name="deleteclass"),
    path('parentsevenings/', views.ParentsEveningsView.as_view(), name="parentsevenings"),
    path('parentsevenings/add', views.AddParentsEveningView.as_view(), name="addparentsevening"),
    re_path(r'^parentsevenings/edit/(?P<pe_id>[0-9]+)$', views.EditParentsEveningView.as_view(), name="editparentsevening"),
    re_path(r'^parentsevenings/delete/(?P<pe_id>[0-9]+)$', views.DeleteParentsEveningView.as_view(), name="deleteparentsevening"),
]
