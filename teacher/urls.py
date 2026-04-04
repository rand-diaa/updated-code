from django.urls import path
from teacher import views
from django.contrib.auth.views import LoginView

urlpatterns = [
path('teacherclick', views.teacherclick_view),
path('teacherlogin', LoginView.as_view(template_name='teacher/teacherlogin.html'),name='teacherlogin'),
path('afterlogin', views.teacher_afterlogin_redirect, name='teacher-afterlogin'),
path('teachersignup', views.teacher_signup_view,name='teachersignup'),
path('teacher-dashboard', views.teacher_dashboard_view,name='teacher-dashboard'),
path('teacher-profile', views.teacher_profile_view, name='teacher-profile'),
path('teacher-view-students', views.teacher_view_students_view,name='teacher-view-students'),
path('teacher-exam', views.teacher_exam_view,name='teacher-exam'),
path('teacher-add-exam', views.teacher_add_exam_view,name='teacher-add-exam'),
path('teacher-view-exam', views.teacher_view_exam_view,name='teacher-view-exam'),
path('teacher-add-question', views.teacher_add_question_view,name='teacher-add-question'),
path('delete-exam/<int:pk>', views.delete_exam_view,name='delete-exam'),
]