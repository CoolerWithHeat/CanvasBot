from django.contrib import admin
from django.urls import path
from DatabaseManagement import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('CreateStudent/', views.create_student),
    path('UpdateStudent/<int:chat_id>/', views.update_student),
    path('CreateCourse/', views.create_course),
    path('GetStudents/<int:chat_id>/', views.get_students),
    path('ReloadStudent/<int:chat_id>/', views.ReloadStudent),
    path('DeleteStudent/<int:chat_id>/', views.DeleteStudent),
]