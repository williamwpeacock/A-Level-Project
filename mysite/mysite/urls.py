from django.urls import path, include

urlpatterns = [
    path('', include('login.urls')),
    path('student/', include('student.urls')),
    path('teacher/', include('teacher.urls')),
    path('parent/', include('parent.urls')),
    path('admin/', include('admin.urls')),
]
